from fastapi import FastAPI
from fastapi import Request
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import db_helper
from pydantic import BaseModel
from typing import Union
from typing import Optional
from typing import List
from fastapi.staticfiles import StaticFiles
import random
# import respuestas
# import logging
import generic_helper
app = FastAPI()


#app.mount('/inicio', StaticFiles(directory='inicio'), name='inicio')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Reemplaza "port" por el puerto de tu aplicación Flutter
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get('/')
async def read_root():
    return {'message': 'Hello from FatAPI'}

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str = ""

@app.post("/login")
def login(request: Request, login_request: LoginRequest):
    # Accede al nombre de usuario y contraseña desde la solicitud
    username = str(login_request.username)
    password = str(login_request.password)

    # Normaliza las cadenas para hacer la comparación insensible a mayúsculas y minúsculas
    username = username.casefold()
    password = password.casefold()

    # Ahora puedes utilizar las variables username y password en tu lógica de autenticación
    # Por ejemplo, puedes verificar si corresponden a un usuario válido en tu base de datos
    respuesta_db = db_helper.obtener_datos_usuarios(username, password)

    if respuesta_db == 1:

        rol_usuario = db_helper.obtener_rol_usuario(username)
        id_usuario = db_helper.obtener_id_usuario(username)  # Agregar esta función

        if rol_usuario is not None:

            return {"message": "Inicio de sesión exitoso", "data": respuesta_db, "username": username, "role": rol_usuario, "user_id": id_usuario}
        else:
            return JSONResponse(content={"message": "Error al obtener el rol del usuario"}, status_code=500)
    else:
        return {"message": "Vuelva a Intentarlo", "data": respuesta_db, "username": "", "role": "", "user_id": 0}


@app.get("/get_user_list")
def get_user_list():
    # Obtener la lista de usuarios desde la base de datos
    user_list = db_helper.obtener_usuarios()

    # Retornar la lista de usuarios como respuesta JSON
    return JSONResponse(content={"userList": user_list})

class EliminarUsuarioRequest(BaseModel):
    nombre_usuario: str

@app.post("/eliminar_usuario", response_model=dict)
async def eliminar_usuario(request: Request, request_body: EliminarUsuarioRequest):
    # Recuperar el nombre de usuario desde los datos enviados desde el frontend
    nombre_usuario = request_body.nombre_usuario

    if not nombre_usuario:
        raise HTTPException(status_code=400, detail="Nombre de usuario no proporcionado")

    # Intentar eliminar el usuario en la base de datos
    try:
        db_helper.eliminar_usuario(nombre_usuario)
        return {"message": f"Usuario '{nombre_usuario}' eliminado correctamente"}
    except Exception as e:
        return {"message": f"Error al eliminar usuario: {str(e)}"}

class RegistrarUsuarioRequest(BaseModel):
    nombre: str
    contrasena: str
    rol: str

@app.post("/registrar_usuario", response_model=dict)
async def registrar_usuario(request_body: RegistrarUsuarioRequest):
    # Recuperar los datos del nuevo usuario desde los datos enviados desde el frontend
    nombre = request_body.nombre
    contrasena = request_body.contrasena
    rol = request_body.rol

    if not nombre or not contrasena or not rol:
        raise HTTPException(status_code=400, detail="Nombre de usuario, contraseña o rol no proporcionados")

    # Validar que el rol sea U o A
    if rol not in ('U', 'A'):
        raise HTTPException(status_code=400, detail="Rol inválido")

    # Intentar registrar el nuevo usuario en la base de datos
    try:
        db_helper.registrar_usuario(nombre, contrasena, rol)
        return {"message": f"Usuario '{nombre}' registrado correctamente"}
    except Exception as e:
        return {"message": f"Error al registrar usuario: {str(e)}"}

class EditarUsuarioRequest(BaseModel):
    nombre_usuario: str
    nuevo_nombre: str
    nueva_contrasena: str
    nuevo_rol: str

@app.post("/editar_usuario", response_model=dict)
async def editar_usuario(request_body: EditarUsuarioRequest):
    # Recuperar los datos para editar el usuario desde los datos enviados desde el frontend
    nombre_usuario = request_body.nombre_usuario
    nuevo_nombre = request_body.nuevo_nombre
    nueva_contrasena = request_body.nueva_contrasena
    nuevo_rol = request_body.nuevo_rol

    if not nombre_usuario or not nuevo_nombre or not nueva_contrasena or not nuevo_rol:
        raise HTTPException(status_code=400, detail="Todos los campos deben ser proporcionados")

    # Validar que el nuevo rol sea U o A
    if nuevo_rol not in ('U', 'A'):
        raise HTTPException(status_code=400, detail="Rol inválido")

    # Intentar editar el usuario en la base de datos
    try:
        db_helper.editar_usuario(nombre_usuario, nuevo_nombre, nueva_contrasena, nuevo_rol)
        return {"message": f"Usuario '{nombre_usuario}' editado correctamente"}
    except Exception as e:
        return {"message": f"Error al editar usuario: {str(e)}"}

class ScoreRequest(BaseModel):
    score: Union[int, str]

@app.post('/puntaje')
async def receive_score(score_request: ScoreRequest):
    print('Recibido:', score_request.dict())
    score = score_request.score
    message = get_message_from_score(score)
    return {'message': message}

def get_message_from_score(score: int) -> str:
    if 0 <= score <= 21:
        return 'baja ansiedad'
    elif 22 <= score <= 35:
        return 'ansiedad moderada'
    elif score >= 36:
        return 'niveles de ansiedad potencialmente preocupantes'
    else:
        return 'Error en el puntaje'

class ScoreDRequest(BaseModel):
    scored: Union[int, str]
    lastCheckboxTotal: Union[int, str]

@app.post('/puntajed')
async def receive_score(scored_request: ScoreDRequest):
    print('Recibido:', scored_request.dict())
    scored = scored_request.scored
    lastCheckboxTotal = scored_request.lastCheckboxTotal
    message = get_messages_from_score_d(scored, lastCheckboxTotal)
    return {'message': message}

def get_messages_from_score_d(scored: int, lastCheckboxTotal: int) -> str:
    if scored < 16:
        return 'Sin sintomas clinicamente significativos de episodio de depresion mayor'
    elif scored > 16 and lastCheckboxTotal >= 5:
        return 'Sintomas clinicamente significativos de episodio de depresion mayor'
    elif scored > 16 and lastCheckboxTotal == 4:
        return  'Episodio de depresion mayor altamente probable'
    elif scored > 16 and lastCheckboxTotal == 3:
        return  'Posible episodio de depresión mayor'
    elif scored >= 16 and lastCheckboxTotal <= 2:
        return 'Episodio depresivo sub-umbral'

#-------------------------------------ACTUALIZAR NOTAS--------------------------------------------

class NotasRequest(BaseModel):
    id_usuario: int
    nota_ansiedad: Optional[str] = None
    nota_depresion: Optional[str] = None
    nota_tecnicas: Optional[str] = None
    nota_sintomas_ansiedad: Optional[str] = None
    nota_sintomas_depresion: Optional[str] = None


@app.post("/actualizar_notas", response_model=dict)
async def actualizar_notas(request: Request, notas_request: NotasRequest):
    # Recuperar los datos desde el cuerpo de la solicitud
    id_usuario = notas_request.id_usuario
    nota_ansiedad = notas_request.nota_ansiedad
    nota_depresion = notas_request.nota_depresion
    nota_tecnicas = notas_request.nota_tecnicas
    nota_sintomas_ansiedad = notas_request.nota_sintomas_ansiedad
    nota_sintomas_depresion = notas_request.nota_sintomas_depresion

    if not any([nota_ansiedad, nota_depresion, nota_tecnicas, nota_sintomas_ansiedad, nota_sintomas_depresion]):
        raise HTTPException(status_code=400, detail="Se debe proporcionar al menos una nota para actualizar")

    try:
        # Obtener las notas actuales del usuario
        notas_actuales = db_helper.obtener_notas_usuario(id_usuario)

        # Actualizar las notas recibidas manteniendo los valores actuales si no se proporcionan
        nueva_nota_ansiedad = nota_ansiedad if nota_ansiedad is not None else notas_actuales.get("nota_ansiedad", "")
        nueva_nota_depresion = nota_depresion if nota_depresion is not None else notas_actuales.get("nota_depresion", "")
        nueva_nota_tecnicas = nota_tecnicas if nota_tecnicas is not None else notas_actuales.get("nota_tecnicas", "")
        nueva_nota_sintomas_ansiedad = nota_sintomas_ansiedad if nota_sintomas_ansiedad is not None else notas_actuales.get("nota_sintomas_ansiedad", "")
        nueva_nota_sintomas_depresion = nota_sintomas_depresion if nota_sintomas_depresion is not None else notas_actuales.get("nota_sintomas_depresion", "")

        # Actualizar las notas en la base de datos
        db_helper.actualizar_notas_usuario(id_usuario, nueva_nota_ansiedad, nueva_nota_depresion, nueva_nota_tecnicas, nueva_nota_sintomas_ansiedad, nueva_nota_sintomas_depresion)

        return {"message": f"Notas actualizadas correctamente"}
    except Exception as e:
        return {"message": f"Error al actualizar notas: {str(e)}"}

#------------------------------OBTENER NOTAS USUARIOS-----------------------------------------------

class NotasUsuario(BaseModel):
    nombre_usuario: str
    nota_ansiedad: str
    nota_depresion: str
    nota_tecnicas: str
    nota_sintomas_ansiedad: str
    nota_sintomas_depresion: str

@app.get("/obtener_notas_usuarios", response_model=List[NotasUsuario])
async def obtener_notas_usuarios():
    try:
        notas_usuarios = db_helper.obtener_notas_usuarios_2()
        return notas_usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notas de usuarios: {str(e)}")


@app.post("/")
# handle request is our main entry point, and the request is what dialogflow is sending
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    #In dialogFlow output_context is a list so we are taking the element 0 and from that the list
    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    # This dictionary will manage all the intents instead of using too much if statements
    intent_handler_dict = {
        'Ansiedad-Especificas.Intent: aprendiendo-ansiedad': manejar_ansiedad_especificas,
        'Depresion-Especificas.Intent: aprendiendo-depresion': manejar_depresion_especificas,
        'Tecnicas-Autorregulacion.Intent: aprendiendo-tecnicas': tecnicas_autorregulacion,
        'Tecnicas-Autorregulacion-Especificas.Intent: aprendiendo-tecnicas': tecnicas_especificas,
        'Contactar-Psicologa.Intent: contactando-psicologa': contacto_psicologa,
        'Reproducir-Video.Intent: mostrando-video': reproducir_video,
        'Abrir-Cuestionario.Intent:abriendo-cuestionario': abrir_cuestionarios
    }

    return intent_handler_dict[intent](parameters, session_id)

def manejar_ansiedad_especificas(parameters: dict, session_id: str):
    try:

        respuestas = {
            "causas": ["La ansiedad puede ser causada por las siguientes condiciones: \n\n"
                       "- Medicamentos \n"
                       "- Medicamentos a base de hierbas \n"
                       "- Abuso de sustancias \n"
                       "- Trauma \n"
                       "- Experiencias malas de la infancia \n"
                       "- Trastornos de pánico",
                       "Por supuesto, acá te dejo algunas de las posibles causas de la ansiedad\n\nLa ansiedad puede surgir debido a diversas circunstancias, que incluyen:\n\n- Uso de medicamentos.\n- Consumo de productos naturales a base de hierbas.\n- Abuso de sustancias.\n- Experiencias traumáticas.\n- Eventos o vivencias de la infancia.\n- La presencia de trastornos de pánico.",
                       "Claro te explico, las causas de la ansiedad suelen ser el resultado de\nuna combinación de influencias biológicas, psicológicas y sociales.\nEsto significa que factores genéticos pueden interactuar con\nsituaciones estresantes o experiencias traumáticas para crear\nproblemas de ansiedad que son importantes desde el punto de vista clínico."],

            "sintomas": [
                "Algunos síntomas que te puedo mencionar son los siguientes:\n\n1. Síntomas cognitivos: Incluyen miedo a perder el control, a sufrir\nlesiones o a volverse loco, pensamientos aterradores, percepción de\nirrealidad, dificultad de concentración y dificultad para hablar.\n 2. Síntomas fisiológicos: Estos abarcan aumento del ritmo cardíaco,\ndificultad para respirar, dolor en el pecho, fatiga, mareos, sudoración, náuseas,\ntemblores, entumecimiento, debilidad, musculos tensos y boca seca.\n 3. Síntomas de comportamiento: Comprenden la evitación de\namenazas, el escape, la búsqueda de seguridad, la inquietud y la\ndificultad para hablar.\n 4. Síntomas afectivos: Involucran sentirse nervioso, asustado, \nfrustrado e irritado.",
                "Con gusto, aquí tienes algunos síntomas de la ansiedad\n\n1. Pensamientos asustados: Preocupación extrema por cosas malas\nque podrían pasar, miedo de volverse loco o preocupación exagerada\npor lo que piensen los demás.\n 2. Sensaciones físicas incómodas: Sentir el corazón latiendo rápido,\ndificultad para respirar, dolor en el pecho, mareos, fatiga, sudoración excesiva,\ntemblores, tension en los musculos y sensación de hormigueo en el cuerpo.\n 3. Comportamientos de evitación: Tratar de evitar situaciones o cosas\nque te asusten, como lugares abarrotados o hablar en público.\n 4. Sentimientos: Sentirse muy nervioso o incluso irritado, tenso o asustado."],

            "tipos": [
                "hay varios tipos de trastornos de ansiedad:\n\n1. Trastorno de ansiedad por separación: Esto sucede cuando alguien tiene un miedo extremo y preocupación por separarse de personas a las que está muy apegado, como sus padres. Pueden experimentar pesadillas y problemas físicos debido a este miedo.\n 2. Mutismo selectivo: En este trastorno, una persona no puede hablar en ciertas situaciones sociales, incluso si es capaz de hablar en otras circunstancias y entiende el idioma.\n 3. Fobia específica: Las personas con fobias específicas tienen un miedo intenso a cosas o situaciones particulares, como animales, inyecciones de sangre, lesiones o ciertos lugares. Este miedo es a menudo desproporcionado al peligro real.\n 4. Trastorno de ansiedad social: Aquí, alguien siente un miedo intenso en situaciones sociales, donde teme ser evaluado negativamente o avergonzado por otros.\n 5. Trastorno de pánico: Las personas con este trastorno experimentan ataques de pánico repentinos e intensos, acompañados de síntomas físicos y temor a tener otro ataque. A menudo evitan situaciones que temen que puedan desencadenar un ataque de pánico.\n 6. Agorafobia: En este trastorno, las personas temen situaciones en las que pueden sentirse atrapadas o sin ayuda, como usar el transporte público o estar en espacios abiertos.\n 7. Trastorno de ansiedad generalizada: Se caracteriza por una preocupación excesiva y persistente sobre muchas áreas de la vida, acompañada de síntomas como nerviosismo, fatiga y problemas para concentrarse. Este transtorno es una causa común de discapacidad laboral.\n 8. Trastorno de ansiedad inducido por sustancias/medicamentos: Los síntomas de ansiedad pueden surgir debido al uso de sustancias o medicamentos, o durante la abstinencia.\n 9. Trastorno de ansiedad debido a otras afecciones médicas: La ansiedad puede ser causada por problemas médicos, como trastornos endocrinos, cardiovasculares, respiratorios, metabólicos o neurológicos.\n\n Estos son diferentes tipos de trastornos de ansiedad, cada uno con sus características específicas.",
                "Existen diferentes tipos de trastornos de ansiedad que pueden afectar a\nlas personas. Estos trastornos causan preocupación y miedo excesivos\nen situaciones específicas. Aquí te explico algunos de ellos de manera\nmás sencilla:\n\n• Trastorno de ansiedad por separación: Algunas personas tienen un\nmiedo muy grande a separarse de las personas a las que están muy\nunidas, como sus padres. Esto puede causarles preocupación y\nnerviosismo.\n• Mutismo selectivo: En algunos casos, las personas no pueden hablar\nen situaciones sociales, como en la escuela o en grupos de personas,\naunque puedan hablar en otras ocasiones.\n• Fobia específica: Hay personas que tienen miedo a cosas o situaciones\nespecíficas, como animales, inyecciones o ciertos lugares, y evitan\nestas cosas a toda costa.\n• Trastorno de ansiedad social: Algunas personas sienten mucho miedo\nen situaciones sociales, como hablar en público o conocer a nuevas\npersonas, porque temen que los demás los juzguen o critiquen.\n• Trastorno de pánico: Esto implica tener ataques de miedo repentinos\nque vienen con síntomas físicos intensos, como el corazón acelerado o\ndificultad para respirar.\n• Agorafobia: Algunas personas tienen miedo a estar en lugares públicos\no abiertos, como el transporte público o grandes multitudes, porque les\npreocupa que no puedan escapar si se sienten mal.\n• Trastorno de ansiedad generalizada: Aquí, las personas se preocupan\nmucho y todo el tiempo sobre muchas cosas diferentes, lo que les\ndificulta concentrarse y les causa nerviosismo. Este transtorno es una causa común de discapacidad laboral\n• Trastorno de ansiedad debido a sustancias o medicamentos: A veces,\nla ansiedad es causada por el uso de drogas o medicamentos.\n• Trastorno de ansiedad debido a otras afecciones médicas: En\nocasiones, la ansiedad es el resultado de problemas de salud física,\ncomo problemas de tiroides o enfermedades del corazón.\n• Espero que esto te ayude a entender mejor qué son los trastornos de\nansiedad."],

            "diagnosticos": [
                'Para la evaluación de la ansiedad, se usan algunas test como el "Test Anxiety\nScale" de Sarason, el "Test Anxiety Inventory" de Spielberger, "Reactions To\nTest" de Sarason, el "German Test Anxiety Inventory" de Hoddap, el "Inventario\nde Situaciones y Respuestas de Ansiedad" de Miguel Tobal y Cano Vindel, el\n"Cuestionario de Ansiedad en los Exámenes" de Valero, la "Cognitive Test\nAnxiety Scale" de Cassady y Jonson, y el "Cuestionario de Ansiedad y\nRendimiento" de Ferrando Varea y Lorenzo.\n\n Cada uno de estos cuestionarios se enfoca en diferentes aspectos de la\nansiedad ante los exámenes, como las preocupaciones, emociones,\n respuestas conductuales y situaciones que generan ansiedad. Se utilizaron\npara comprender mejor cómo afecta la ansiedad a los estudiantes en\nsituaciones de evaluación.',
                'Para evaluar la ansiedad en situaciones de evaluación, se emplean diversos\ncuestionarios, como el "Test Anxiety Scale" desarrollado por Sarason, el "Test\nAnxiety Inventory" de Spielberger, y otros como el "Cuestionario de Ansiedad\nen los Exámenes" de Valero, el "Inventario de Situaciones y Respuestas de\nAnsiedad" de Miguel Tobal y Cano Vindel, el "German Test Anxiety Inventory"\nde Hoddap, la "Cognitive Test Anxiety Scale" de Cassady y Jonson, así como\nel "Cuestionario de Ansiedad y Rendimiento" de Ferrando Varea y Lorenzo.\n\n Cada uno de estos cuestionarios se centra en diferentes aspectos de la\nansiedad relacionados con las evaluaciones, como las preocupaciones, las\nemociones experimentadas, las respuestas conductuales y las situaciones\nque generan ansiedad. Estas herramientas se utilizan para obtener una\ncomprensión más completa de cómo la ansiedad afecta a los estudiantes\nen situaciones de examen.',
                'En la evaluación de la ansiedad en contextos de exámenes, se utilizan varios\ncuestionarios, como el "Test Anxiety Scale" de Sarason, el "Test Anxiety\nInventory" de Spielberger, entre otros cada uno se enfoca en diferentes\naspectos de la ansiedad, como las preocupaciones y emociones relacionadas\ncon los exámenes.\n\nEstos cuestionarios ayudan a entender cómo la ansiedad afecta a los\nestudiantes en situaciones de evaluación.',
                'Para evaluar la ansiedad en situaciones de exámenes, se emplean diversos\ncuestionarios como el "Test Anxiety Scale" de Sarason, el "Test Anxiety\nInventory" de Spielberger, entre otros. Estos cuestionarios se centran en diferentes\naspectos de la ansiedad relacionados con los exámenes y ayudan a\ncomprender su impacto en los estudiantes.',
                'En la evaluación de la ansiedad durante los exámenes, se utilizan diferentes\ncuestionarios, como el "Test Anxiety Scale" de Sarason o el "Test Anxiety\nInventory" de Spielberger. Cada uno se enfoca en aspectos específicos de la\nansiedad relacionada con las pruebas, permitiendo así comprender mejor\ncómo afecta a los estudiantes en estas situaciones.'],

            "tratamientos": [
                "A continuación, mencionaré algunos de los tratamientos disponibles:\n\nLos ejercicios de relajación y la exposición gradual al entorno escolar son\ndos enfoques terapéuticos para reducir la ansiedad en situaciones\neducativas. Los ejercicios de relajación ayudan a controlar las respuestas\nfísicas, como la frecuencia cardíaca, mientras que la exposición gradual\nimplica enfrentar gradualmente situaciones escolares estresantes para\ndesensibilizar la ansiedad. Ambos métodos son útiles para mejorar la\nconfianza en entornos educativos.",
                "Una alternativa de tratamiento es el enfoque terapéutico basado en juegos:\n\nEste tratamiento utiliza actividades lúdicas y juegos como herramientas para\nabordar los problemas emocionales, conductuales. Este enfoque se basa\nla idea de que se pueden expresar sus pensamientos y emociones de manera\nmás efectiva a través del juego, permitiéndoles abordar sus dificultades en un\nambiente terapéutico seguro y atractivo.",
                "Algunos tratamientos que existen son los siguientes:\n\nTratamiento para la ansiedad relacionada con el rechazo escolar que implica\nla evitación de situaciones sociales aversivas incluye técnicas terapéuticas\ncomo la reestructuración cognitiva y el modelado. Estas estrategias se\nutilizan para ayudar a los niños o adolescentes a manejar su ansiedad y\nsuperar el rechazo escolar, abordando sus pensamientos y comportamientos\nen situaciones sociales desafiantes.",
                "Claro, entro de las posibles alternativas de tratamiento se encuentran las siguientes:\n\nEl tratamiento efectivo para la ansiedad incluye el entrenamiento en\nhabilidades sociales, que implica el modelado de comportamientos\nadecuados, el role-playing para practicar interacciones sociales, y la\nreestructuración cognitiva para cambiar pensamientos negativos.\nAdemás, se utilizala exposición gradual para enfrentar situaciones sociales\ntemidas y mejorar las habilidades en interacciones sociales."],

            "prevención": [
                "Aca te menciono algunas estrategias para prevenir la ansiedad:\n\nEducación sobre la ansiedad: Proporcionar a los niños y adolescentes\ninformación sobre la ansiedad, sus causas y sus efectos, para que\ncomprendan mejor sus propios sentimientos y reacciones.\n\nEntrenamiento en técnicas de control de la activación: Enseñar a los\njóvenes técnicas de relajación y manejo del estrés para ayudarles a\ngestionar sus niveles de ansiedad.\n\nDetección y sustitución de pensamientos automáticos negativos: Ayudar\na los participantes a identificar y cambiar patrones de pensamiento negativos\nque contribuyen a la ansiedad.\n\nAutorreforzamiento abierto y encubierto: Promover la autoevaluación y el\nrefuerzo de conductas positivas y saludables que reduzcan la ansiedad.\n\nEntrenamiento en solución de problemas: Enseñar habilidades para abordar\nsituaciones estresantes y resolver problemas de manera efectiva.\n\nExposición gradual: Ayudar a los participantes a enfrentar gradualmente las\nsituaciones o estímulos que les generan ansiedad, de manera controlada y\nsegura.",
                "Puedo ofrecerte algunas técnicas que pueden ayudarte a prevenir y manejar\nla ansiedad como:\n\nTécnicas cognitivo-conductuales: Estas técnicas se centran en modificar\npensamientos disfuncionales y comportamientos asociados con la ansiedad.\nAlgunas estrategias mencionadas incluyen el entrenamiento de relajación\nprogresiva, control de la respiración, exposición gradual a situaciones que\ncausan ansiedad y técnicas de autocontrol.\n\nTécnicas psicodinámicas: Estas técnicas buscan comprender y abordar la\nansiedad a través de un enfoque empático y de exploración de las emociones\ny las ansiedades del individuo. Un ejemplo es la terapia interpersonal.\n\nOtras técnicas: Se mencionan enfoques como el Counselling (consejo\nasistido), que implica analizar los problemas, comprenderlos y establecer\nobjetivos y metas, así como la terapia familiar breve, que se enfoca en el\ncambio en el ámbito familiar para resolver problemas."]
        }

        ansiedad_especificas = parameters.get('ansiedad-especificas', None)

        if ansiedad_especificas is not None and ansiedad_especificas[0] in respuestas:
            categoria = ansiedad_especificas[0]
            respuesta_random = random.choice(respuestas[categoria])
            fulfillment_text = respuesta_random
        else:
            fulfillment_text = "La palabra no coincide."

        # Crea la respuesta JSON
        response_data = {
            "fulfillmentText": fulfillment_text
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Lo siento, no pude entender tu pregunta."})

def manejar_depresion_especificas(parameters: dict, session_id: str):
    try:

        respuestas2 = {
            "causas": ["Ahora, permíteme abordar las posibles causas:\n\n- Genes.\n- Personalidad.\n- Familia.\n- Género.\n- Estilo.\n- Estilo de pensamiento.\n- Enfermedades crónicas.\n- Problemas económicos.",
                       "A continuación, explicaré algunas de sus causas:\n\n- Estrés y sucesos vitales estresantes.\n- Presencia de una enfermedad física.\n- Administración de algunos fármacos.",
                       "Por supuesto, déjame darte más detalles sobre las causas:\n\n- Haber pasado por episodios depresivos previos.\n- Tener antecedentes familiares de depresión.\n- Enfrentar situaciones estresantes o traumáticas, como la pérdida de un\n ser querido o problemas en las relaciones interpersonales.\n- Circunstancias como enfermedades físicas graves y consumo de ciertas\n medicinas, así como abuso de sustancias, que pueden aumentar la\n vulnerabilidad a la depresión.\n- En el caso de algunas mujeres, el período postparto puede ser un factor\n de riesgo.",
                       "Se considera que hay diversos factores implicados en las causas como:\n\n- Factores relacionados con la personalidad del paciente, inseguridad,\n dependencia, hipocondría, perfeccionismo, autoexigencia\n- Factores ambientales. Sufrir algún problema económico, familiar y de salud.\n- Factores biológicos. Sobre este punto, se deben destacar diversos aspectos.\n- Cambios en el Cerebro: La depresión está relacionada con ciertos problemas\n en partes importantes del cerebro.\n- Problemas de Comunicación en el Cerebro: En la depresión, la forma en que\n las células cerebrales se comunican no es efectiva.\n- Influencia Familiar: Si algún familiar ha tenido depresión, es más probable\n que tú también la tengas debido a ciertos genes."],

            "sintomas": ["A continuación, te presento información sobre los síntomas de la depresión:\n\n1. Permanecer en un estado de tristeza durante la mayor parte del día,\n  prácticamente todos los días.\n2. Perder el interés en las actividades que solían brindar placer.\n3. Experimentar variaciones en el apetito o el peso.\n4. Enfrentar dificultades para conciliar el sueño o mantener un patrón\n  de sueño regular.\n5. Sentir una disminución en la velocidad o experimentar inquietud.\n6. Experimentar una notable falta de energía.\n7. Sentir desesperanza o una baja autoestima.\n8. Tener problemas para enfocarse o concentrarse en tareas.\n9. Experimentar pensamientos recurrentes sobre la muerte o el suicidio.",
                         "Claro, los sintomas frecuentes de la depresión incluyen lo siguiente:\n\n- Persistente sensación de tristeza, ansiedad o un profundo vacío emocional.\n- Sentimiento de desesperanza o una visión pesimista del futuro.\n- Experiencia de irritabilidad, frustración o inquietud continuas.\n- Sentimientos de culpabilidad, inutilidad o falta de poder.\n- Pérdida de interés o placer en actividades y pasatiempos habituales.\n- Fatiga, disminución de la energía o sensación de ralentización.\n- Dificultad para concentrarse, recordar o tomar decisiones.\n- Problemas para conciliar el sueño, despertarse temprano o dormir en\n exceso.\n- Cambios en el apetito o peso sin planificación previa.\n- Dolores y molestias, cefaleas, calambres o problemas digestivos sin causa\n física evidente o que no responden al tratamiento.\n- Pensamientos sobre el suicidio o la muerte, o intentos de suicidio.",
                         "Por supuesto, ahora hablaremos sobre los síntomas:\n\n- Tristesa.\n- Pérdida de interés en cosas con las que antes se solía disfrutar.\n- Vacío emocional.\n- Pensamientos negativos.\n- Problemas de concentración o de memoria.\n- Delirios, alucionaciones o ideas de suicidio",
                         "Vamos a explorar ahora los síntomas más comunes:\n\n• Problemas de sueño: Dificultad para conciliar el sueño, despertar precoz o\n  aumento de las horas de sueño.\n• Enlentecimiento mental y físico.\n• Aumento.\n• disminución del apetito Aumento.\n• disminución del peso.\n• Fatiga Estreñimiento.\n• Alteración de la menstruación."],

            "tipos": ['''A continuación, describiré 2 tipos diferentes de depresión:\n\n• Depresión mayor, que implica síntomas de depresión la mayoría del tiempo\n  durante por lo menos dos semanas. Estos síntomas interfieren con la\n  capacidad para trabajar, dormir, estudiar y comer.\n• Trastorno depresivo persistente (distimia), que a menudo incluye síntomas\n  de depresión menos graves que duran mucho más tiempo, generalmente\n  por lo menos durante 2 años.''',
                      "A continuación, veremos distintos tipos de depresión:\n\n- Depresión Reactiva: Aparece debido a situaciones estresantes. Usualmente\n  no requiere medicamentos, solo apoyo emocional. No obstante, si alguien es\n  propenso a la depresión, un evento estresante puede desencadenar una\n  forma más grave de esta condición.\n- Depresión Endógena o Unipolar: Puede repetirse en la vida y suele ser\n  moderada o grave.\n- Distimia: Es un tipo menos severo de depresión que afecta el bienestar y el\n  funcionamiento de la persona.\n- Trastorno Bipolar: No es tan común y se caracteriza por cambios en el\n  estado de ánimo, alternando entre fases de euforia (manía) y períodos \n  de tristeza profunda (depresión).",
                      "Claro, aquí tienes algunos tipos de depresión:\n\n- Depresión Estacional: Es cuando la tristeza y otros síntomas de depresión\n  aparecen en ciertas épocas del año, principalmente durante el otoño e\n  invierno.\n- Depresión Principal: No está relacionada con una enfermedad física o\n  mental, el uso de drogas o ciertos medicamentos.\n- Depresión Secundaria: Sucede como resultado de una enfermedad física o\n  mental, el consumo de drogas o el uso de ciertos medicamentos.\n- Depresión con Síntomas Psicóticos: Además de los síntomas comunes de\n  la depresión, incluye síntomas más intensos como creencias erróneas\n  y experiencias irreales."],

            "diagnosticos": ["Aquí tienes el diagnóstico para la depresión mediante la evaluación de ciertos\ncriterios clínicos estandarizados. Los dos sistemas de clasificación más\n comunes utilizados en el diagnóstico de la depresión son la Clasificación\nEstadística Internacional de Enfermedades y Problemas Relacionados con la\nSalud (CIE) y el Manual Diagnóstico y Estadístico de los Trastornos Mentales.\n\n Criterios Diagnósticos según CIE-10:\n1. Episodio Depresivo Leve:\n   - Duración mínima de dos semanas.\n   - Presencia de al menos dos o tres síntomas típicos de depresión.\n\n2. Episodio Depresivo Moderado:\n   - Duración mínima de dos semanas.\n   - Al menos dos síntomas del criterio B y síntomas somáticos.\n\n3. Episodio Depresivo Grave:\n   - Duración mínima de dos semanas.\n   - Presencia de síntomas graves como pérdida de autoestima, pensamientos\n  suicidas, síntomas psicóticos y otros síntomas somáticos marcados.\n\n Criterios Diagnósticos según DSM-5:\n1. Trastorno Depresivo Mayor:\n   - Presencia de al menos cinco de nueve síntomas durante al menos\n  dos semanas.\n   - Uno de los síntomas debe ser ánimo deprimido o pérdida de\n s interés o placer.\n   - Causa malestar significativo o deterioro en áreas importantes de la vida."],

            "tratamientos": ["Por supuesto, estos son algunos de los tratamientos que se usan para combatir la depresión:\n\n- Medicamentos:\n  - Antidepresivos: Modifican la producción o utilización de ciertas sustancias\n   químicas cerebrales relacionadas con el estado de ánimo y el estrés.\n   Pueden requerir probar varios antes de encontrar el más efectivo con los\n   menores efectos secundarios.\n\n- Psicoterapias:\n   - Terapia cognitivo-conductual (TCC): Ayuda a modificar pensamientos y\n   comportamientos negativos que contribuyen a la depresión.\n  - Terapia interpersonal (IPT): Se centra en mejorar las relaciones\n   interpersonales y la forma en que uno se relaciona con los demás.\n\n- Terapias de Estimulación Cerebral:\n  - Estimulación Magnética Transcraneal (RTMS): Utiliza campos magnéticos\n   para activar áreas específicas del cerebro.\n  - Terapia Electroconvulsiva (TEC): Implica la inducción de convulsiones\n   controladas mediante electricidad para aliviar los síntomas."],

            "prevención": [" Aquí te detallo estos 3 enfoques para la Prevención:\n\n1. Prevención Primaria:\n   - Objetivo: Evitar la aparición de la enfermedad.\n   - Enfoque: Dirigido a la población en general o a grupos específicos no\n   identificados como de alto riesgo.\n   - Ejemplo en salud mental: Programas de educación y concienciación sobre\n   salud mental en comunidades.\n\n2. Prevención Secundaria:\n   - Objetivo: Detectar y tratar precozmente la enfermedad.\n   - Enfoque: Dirigido a individuos o grupos con riesgo superior al promedio.\n   - Ejemplo en salud mental: Evaluación temprana y tratamiento de\n   síntomas depresivos en personas con antecedentes familiares de\n   trastornos mentales.\n\n3. Prevención Terciaria:\n   - Objetivo: Reducir la discapacidad y rehabilitar a las personas afectadas\n   por la enfermedad.\n   - Enfoque: Dirigido a individuos que ya tienen la enfermedad.\n   - Ejemplo en salud mental:  Programas de rehabilitación psicosocial para\n   personas que han experimentado episodios depresivos graves.",
                           "Ahora, exploraremos enfoques basado en la reducción del riesgo de la depresión:\n\n1. Intervención Universal:\n   - Objetivo: Dirigida a toda la población o a la población general no\n   identificada como de alto riesgo.\n   - Enfoque: Proporciona información y estrategias para reducir el riesgo en la\n   población en general.\n   - Ejemplo en salud mental: Campañas de sensibilización sobre manejo\n   del estrés y bienestar emocional.\n\n2. Intervención Selectiva:\n   - Objetivo: Dirigida a grupos específicos con un riesgo más alto\n   que la población general.\n   - Enfoque: Proporciona intervenciones específicas para reducir el riesgo\n   en grupos identificados como de mayor riesgo.\n   - Ejemplo en salud mental: Programas de apoyo psicosocial para\n   adolescentes en entornos escolares con altos niveles de estrés.\n\n3. Intervención Indicada:\n   - Objetivo: Dirigida a individuos con riesgo alto y síntomas incipientes,\n   pero que aún no cumplen con los criterios de diagnóstico.\n   - Enfoque: Ofrece intervenciones focalizadas en aquellos que ya muestran\n   signos tempranos de la enfermedad.\n   - Ejemplo en salud mental: Terapia temprana para personas que muestran\n   síntomas de ansiedad pero aún no cumplen los criterios de un trastorno de\n   ansiedad."]
        }

        ansiedad_especificas = parameters.get('ansiedad-especificas', None)

        if ansiedad_especificas is not None and ansiedad_especificas[0] in respuestas2:
            categoria = ansiedad_especificas[0]
            respuesta_random = random.choice(respuestas2[categoria])
            fulfillment_text = respuesta_random
        else:
            fulfillment_text = "La palabra no coincide."

        # Crea la respuesta JSON
        response_data = {
            "fulfillmentText": fulfillment_text
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Perdón, no logro entender tu pregunta."})

def tecnicas_autorregulacion(parameters: dict, session_id: str):
    try:

        respuestas3 = {
            "ansiedad": ['¡Por supuesto!, ahora te muestro algunas técnicas para la ansiedad:\n\n- Respiración Controlada\n- Mindfulness y Meditación\n- Ejercicio Físico Regular\n- Técnicas de Relajación\n- Practica de la greatitud\n- Técnica de la visualización',
                         '¡Claro!, aquí están algunas de las técnicas para la manejar la ansiedad\n\n- Regulación de la Respiración\n- Plenitud Mental y Atención Plena\n- Mantener un Ejercicio Físico Consistente\n- Prácticas para la Relajación\n- Practicar la gratitud\n- Técnica de la visualización',
                         '¡De acuerdo!, a continuación, algunas de las técnicas que pueden serte utiles para manejar la ansiedad:\n\n- Control de la Respiración\n- Mindfulness y Plenitud Mental\n- Mantenimiento de un Régimen de Ejercicio Físico Regular\n- Ejercicios de Relajación\n- La practica de la gratitud\n- Técnica de la visualización'],

            "depresión": ['Entiendo, aquí tienes algunas técnicas para manejar la depresión:\n\n- Actividad Física Regular\n- Pensamiento inverso\n- Práctica de la conciencia plena (mindfulness)\n- Practica de la gratitud',
                          'Claro, a continuación, te detallo varias estrategias para manejar la depresión:\n\n- Mantener una Rutina de Ejercicio Físico Constante\n- Cambiar la Dirección de los Pensamientos\n- Practicar la Atención Plena (mindfulness)\n- Aplicar la practica de la gratitud',
                          'Claro, aquí te presento algunas estrategias para que puedes controlar la depresión:\n\n- Mantener una Rutina de Ejercicio Físico\n- Cambio de Perspectiva en los Pensamientos\n- Ejercitar la Atención Plena (mindfulness)\n- Practicar la gratitud']

        }

        condiciones = parameters.get('condiciones', None)

        if condiciones is not None and condiciones[0] in respuestas3:
            categoria = condiciones[0]
            respuesta_random = random.choice(respuestas3[categoria])
            fulfillment_text = respuesta_random
        else:
            fulfillment_text = "La palabra no coincide."

        # Crea la respuesta JSON
        response_data = {
            "fulfillmentText": fulfillment_text
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Ocurrió un error en el servidor."})


def tecnicas_especificas(parameters: dict, session_id: str):
    try:

        respuestas4 = {
            "Respiración Controlada": ['¡Claro! Ahora te explico cómo realizar la técnica de respiración controlada:\n\nLa respiración controlada implica ajustar conscientemente la frecuencia y profundidad de la respiración para influir en el sistema nervioso y lograr efectos beneficiosos en el cuerpo y la mente.\n\n1. Respirar 6 veces por minuto.\n 2. Tiempo espiratorio doble que el inspiratorio.\n 3. Respiración predominante abdominal.\n 4. Respirar con los labios casi unidos para permitir que un poco de aire permaneciera en los pulmones\n hasta el final de la espiración.',
                                       'Claro, a continuación te explico cómo aplicar la técnica de respiración controlada:\n\nLa técnica de respiración controlada implica de manera consciente adaptar la frecuencia y la profundidad de la respiración. Esto tiene el propósito de influir en el sistema nervioso y obtener efectos beneficiosos en el cuerpo y la mente.\n\n1. Realizar 6 respiraciones en un lapso de un minuto.\n2. Asegurar que la duración de la espiración sea el doble de la inspiración.\n3. Centrarse en una respiración mayormente abdominal.\n4. Mantener los labios casi unidos durante la respiración para permitir que un poco de aire permanezca en los pulmones hasta concluir la espiración.',
                                       'Por supuesto, ahora te describiré cómo ejecutar la técnica de respiración controlada:\n\nLa respiración controlada implica ser consciente de ajustar tanto la frecuencia como la profundidad de la respiración. Esto se hace para influir en el sistema nervioso y obtener efectos positivos tanto en el cuerpo como en la mente.\n\n1. Realizar 6 respiraciones por minuto.\n2. Mantener el tiempo de espiración el doble que el de inspiración.\n3. Hacer hincapié en la respiración abdominal predominante.\n4. Durante la respiración, mantener los labios casi juntos para permitir que un poco de aire permanezca en los pulmones hasta el final de la espiración.'],

            "Mindfulness y Meditación": ['Por supuesto. A continuación, te detallo como hacer la técnica de mindfulness y meditación:\n\nMindfulness es estar plenamente presente, consciente de pensamientos, emociones y entorno y la meditación de mindfulness comienza con la concentración en un punto, como la respiración, para calmar la mente y encontrar serenidad.\n\n1. Adopta una posición cómoda, ya sea sentado o acostado.\n2. Cerremos los ojos si así nos sentimos más cómodos.\n3. Enfócate en la respiración, sintiendo el movimiento del estómago al inhalar y exhalar.\n4. Sigue cada inhalación y exhalación como si fueran olas.\n5. Cuando nuestra mente se distraiga, volvamos al estómago y a la sensación de respirar.\n6. Si esto ocurre repetidamente, solo volvamos a la respiración, sin importar la distracción.\n7. Practiquemos 15 minutos diarios, observando cómo nos afecta incorporar esta disciplina en nuestra vida.',
                                         'Claro, a continuación, te explico cómo realizar la técnica de mindfulness y meditación:\n\nMindfulness implica mantener plena consciencia del momento actual, estando atento a los pensamientos, emociones y al entorno. Por otro lado, la meditación de mindfulness inicia centrándose en un punto focal, como la respiración, con el propósito de tranquilizar la mente y encontrar serenidad.\n\n1. Encuentra una posición cómoda, ya sea sentado o acostado.\n2. Si te sientes bien, cierra los ojos.\n3. Presta atención a tu respiración, siente cómo tu barriga sube y baja con cada inhalación y exhalación.\n4. Imagina que estás siguiendo el ritmo de las olas mientras respiras.\n5. Si tu mente divaga, regresa a sentir tu barriga y la forma en que respiras.\n6. Si esto sucede a menudo, no te preocupes, simplemente vuelve a centrarte en tu respiración.\n7. Intenta dedicar 15 minutos cada día a esto y observa cómo te hace sentir en tu vida diaria.\n¡Espero que lo disfrutes!',
                                         'Por supuesto, ahora te explicaré cómo llevar a cabo la técnica de mindfulness y meditación:\n\nMindfulness implica la plena presencia y conciencia de nuestros pensamientos, emociones y el entorno en el momento presente. La meditación de mindfulness se inicia centrándose en un punto específico, como la respiración, con el objetivo de tranquilizar la mente y encontrar la serenidad.\n\n1. Busca una posición cómoda, sentado o acostado, lo que prefieras.\n2. Si te sientes bien haciéndolo, cierra los ojos.\n3. Enfócate en tu respiración, siente cómo tu estómago sube y baja con cada inhalación y exhalación.\n4. Imagina que estás siguiendo el vaivén de las olas mientras respiras.\n5. Si tu mente divaga, vuelve gentilmente a concentrarte en tu estómago y en tu respiración.\n6. Si esto sucede varias veces, no te preocupes, simplemente regresa a la respiración.\n7. Intenta hacer esto durante 15 minutos cada día y observa cómo te sientes en tu vida cotidiana.\n¡Espero que disfrutes de esta práctica!'],

            "Ejercicio Físico": ['¡Excelente! Aquí te menciono cómo llevar a cabo las técnicas de ejercicio físico regular:\n\nEl ejercicio físico tiene un impacto positivo en la salud emocional al afectar el sistema nervioso y liberar endorfinas, que son neurotransmisores asociados con la generación de sensaciones de bienestar y la reducción de la depresión y la ansiedad.\n\n1. Ejercicios Cardiovasculares (como andar en bicicleta, correr, nadar):\nElige uno que te guste, como andar en bicicleta o correr por el parque. Comienza despacio y luego ve más rápido.\n\n2. Ejercicios de Fuerza (como flexiones, sentadillas, levantamiento de pesas):\nHaz flexiones (bajando y subiendo tu cuerpo) o sentadillas (dobla tus rodillas y vuelve a ponerte de pie).\n Comienza con poquitas repeticiones y ve agregando más con el tiempo.\n\n3. Flexibilidad y equilibrio (Estiramientos, yoga, taichi, pilates):\nEstira tu cuerpo, como si intentaras tocar tus pies con las manos. Para equilibrarte, puedes pararte en una pierna y luego en la otra.\n\n4. Entrenamiento en circuito (flexiones, sentadillas, saltos y plancha):\nHaz cada uno por un tiempo corto y luego pasa al siguiente ejercicio sin descansar mucho.',
                                 '¡Claro! Aquí te explico cómo realizar ejercicios físicos de manera constante y regular:\n\nLa actividad física tiene un efecto beneficioso en el bienestar emocional al influir en el sistema nervioso y liberar endorfinas. Estas sustancias químicas cerebrales están relacionadas con la generación de sensaciones positivas y la disminución de la depresión y la ansiedad.\n\n1. Actividades Cardiovasculares (como andar en bicicleta, correr, nadar):\nEscoge una que te agrade, como pasear en bicicleta o salir a correr en el parque. Comienza a un ritmo tranquilo y luego aumenta la intensidad gradualmente.\n\n2. Ejercicios de Resistencia (como flexiones, sentadillas, levantamiento de pesas):\nRealiza flexiones (bajando y subiendo tu cuerpo) o sentadillas (doblando tus rodillas y volviendo a la posición inicial). Comienza con pocas repeticiones e incrementa con el tiempo.\n\n3. Flexibilidad y Equilibrio (Estiramientos, yoga, taichi, pilates):\nEstira tu cuerpo, estirando hacia abajo para tocar tus pies con las manos, por ejemplo. Para mejorar tu equilibrio, puedes intentar mantener una pierna levantada y luego cambiar a la otra.\n\n4. Rutina en Circuito (flexiones, sentadillas, saltos y plancha):\nRealiza cada ejercicio por un breve período y luego pasa al siguiente sin descansar mucho entre ellos.',
                                 '¡Por supuesto! Aquí te describo cómo mantener una rutina constante de ejercicio físico regular:\n\nParticipar en actividad física tiene un efecto positivo en el bienestar emocional al influir en el sistema nervioso y liberar endorfinas. Estas sustancias químicas cerebrales están relacionadas con la creación de sensaciones agradables y la disminución de la depresión y la ansiedad.\n\n1. Actividades Cardiovasculares (como bicicleta, correr, natación):\nElige una que te resulte agradable, como andar en bicicleta o correr en el parque. Comienza a un ritmo suave y luego aumenta la intensidad gradualmente.\n\n2. Ejercicios de Resistencia (como flexiones, sentadillas, levantamiento de pesas):\nRealiza flexiones (bajando y subiendo tu cuerpo) o sentadillas (doblando las rodillas y volviendo a la posición inicial).\nComienza con pocas repeticiones e incrementa con el tiempo.\n\n3. Flexibilidad y Equilibrio (Estiramientos, yoga, taichi, pilates):\nEstira tu cuerpo, intentando alcanzar tus pies con las manos, por ejemplo. Para mejorar tu equilibrio, puedes probar pararte en una pierna y luego en la otra.\n\n4. Rutina en Circuito (flexiones, sentadillas, saltos y planchas):\nHaz cada ejercicio durante un corto periodo y luego pasa al siguiente sin descansar demasiado entre cada uno.'],

            "Técnicas de Relajación": ['Con gusto. Aquí está la explicación sobre cómo realizar la técnica de relajación:\n\nEs una técnica que se centra en tensar y luego relajar los músculos del cuerpo para reducir la tensión y promover la relajación.\n\n1. Siéntate cómodamente y apoya tu cabeza en algún punto.\n\n2. Comienza tensionando y relajando los músculos del cuerpo por zonas:\n- Comienza con las manos, antebrazos y bíceps. Aprieta un puño, siente la tensión en los antebrazos y hombros, y luego relájalos para notar la diferencia.\n- Repite el proceso con el otro brazo.\n- Luego, enfócate en la zona de la cabeza, ejercitando los músculos de la cara, cuello y hombros.\n- Continúa con la zona del tórax, estómago y la región lumbar, tensando y relajando los músculos.\n- Finaliza con los muslos, nalgas, pantorrillas y pies.\n\n3. Cuando termines la tensión en los dedos de ambos pies, tómate unos segundos para notar cómo disminuye la pesadez en las extremidades inferiores y cómo la sensación de relajación se extiende por todo el cuerpo.',
                                       'Por supuesto. Aquí te presento cómo aplicar la técnica de relajación:\n\nEs un método que se enfoca en contraer y después liberar la tensión de los músculos del cuerpo para disminuir el estrés y fomentar la calma.\n\n1. Siéntate de forma relajada y apoya tu cabeza en algún lugar cómodo.\n2. Vamos a hacer un ejercicio para liberar la tensión en diferentes partes del cuerpo:\n   - Empecemos con las manos, los antebrazos y los bíceps. Aprieta el puño fuerte, siente la tensión en tus brazos y luego relájalos para sentir cómo cambia la sensación.\n   - Haz lo mismo con el otro brazo.\n   - Después, enfócate en la cara, el cuello y los hombros, como si estuvieras haciendo una mueca divertida.\n    - Sigue con el pecho, el estómago y la parte baja de la espalda, tensando y luego relajando los músculos.\n    - Termina con los muslos, las nalgas, las pantorrillas y los pies.\n 3. Cuando termines de tensar y relajar los dedos de los pies, tómate unos segundos para sentir cómo disminuye la sensación de pesadez en tus piernas y cómo la relajación se extiende por todo tu cuerpo.\n\n ¡Espero que te sientas más relajado!',
                                       'Por supuesto. Aquí te explico cómo aplicar la técnica de relajación progresiva:\n\nEsta técnica se trata de tensar y luego relajar conscientemente los músculos de tu cuerpo para disminuir el estrés y fomentar la calma.\n\n1. Siéntate cómodamente y apoya tu cabeza en algo suave.\n\n2. Vamos a hacer un ejercicio para liberar la tensión:\n   - Empecemos con las manos y los brazos. Aprieta tus manos con fuerza, luego suelta. Repite con el otro brazo.\n   - Luego, realiza algunas expresiones faciales, como fruncir el ceño o sonreír.\n   - Continúa con el pecho, el estómago y la parte baja de la espalda, apretando y luego soltando.\n   - Finaliza apretando y soltando los músculos de los muslos, nalgas, pantorrillas y pies.\n\n3. Cuando hayas terminado, tómate un momento para sentir cómo la tensión disminuye y la relajación se extiende por todo tu cuerpo.'],

            "Practica de la gratitud": ["¡Claro! Aquí te explico cómo llevar a cabo la práctica de gratitud:\n\nLa práctica de gratitud es reconocer y apreciar conscientemente lo positivo en la vida, expresando agradecimiento hacia ello.\n\n1. Reflexiona cada día: Al final de cada día, tómate unos minutos para reflexionar sobre las cosas que te hicieron sentir agradecido, ya sean personas, eventos o experiencias.\n2. Expresa gratitud a otros: Agradece a las personas que conoces. Puedes llamar, enviar un correo electrónico o incluso escribir una carta para expresar tu agradecimiento.\n3. Agradece incluso en pequeños gestos: Dile 'gracias' a personas desconocidas que te brindan ayuda, como al ceder el paso en el tráfico.\n4. Expresa gratitud por tus capacidades: Agradece por las habilidades y capacidades que posees, incluso en momentos difíciles.\n5. Fomenta la gratitud en familia: Comienza un ritual familiar agradeciendo antes de las comidas o compartiendo lo que estás agradecido antes de dormir.\n6. Sé creativo con la gratitud: Encuentra maneras creativas de expresar tu agradecimiento, como planteando un jardín de gratitud o tomando fotos de cosas que te hacen sentir agradecido.",
                                        '¡Por supuesto! Aquí te muestro cómo realizar la práctica de gratitud:\n\nLa práctica de gratitud consiste en reconocer de manera consciente y apreciar las cosas positivas en la vida, expresando agradecimiento hacia ellas.\n\n1. Reflexiona diariamente: Al terminar cada día, tómate unos minutos para reflexionar sobre las cosas que te hicieron sentir agradecido, ya sean personas, eventos o experiencias especiales.\n2. Expresa agradecimiento a otros: No dudes en agradecer a las personas que te rodean. Puedes llamar, enviar un mensaje o incluso escribir una nota para expresar tu agradecimiento.\n3. Valora los pequeños gestos: Agradece incluso en los gestos más pequeños de amabilidad, como cuando alguien te cede el paso en el tráfico o te sostiene la puerta.\n4. Aprecia tus habilidades: Agradece por las habilidades y capacidades que tienes, incluso en momentos desafiantes.\n5. Fomenta la gratitud en familia: Crea una tradición familiar al expresar gratitud antes de las comidas o compartir lo que cada uno está agradecido antes de ir a dormir.\n6. Sé creativo con la gratitud: Encuentra formas creativas de expresar tu agradecimiento, como cultivar un jardín de gratitud o capturar momentos que te inspiren gratitud en fotografías.',
                                        '¡Claro! A continuación, te detallo cómo llevar a cabo la práctica de gratitud:\n\nLa práctica de gratitud implica reconocer y apreciar de manera consciente lo positivo en la vida, expresando agradecimiento hacia ello.\n\n1. Reflexiona diariamente: Al final de cada día, dedica unos minutos a pensar en las cosas que te hicieron sentir agradecido, ya sea por personas, eventos o experiencias que hayan sido significativas.\n2. Demuestra gratitud a los demás: No dudes en expresar tu agradecimiento a las personas de tu vida. Puedes llamar, enviar un mensaje o incluso dejar una nota para mostrar tu aprecio.\n3. Agradece los pequeños gestos: Reconoce y agradece los gestos pequeños de amabilidad, como cuando alguien te da paso en el tráfico o te sostiene la puerta abierta.\n4. Reconoce tus habilidades: Agradece por las habilidades y capacidades que posees, incluso en momentos difíciles.\n5. Promueve la gratitud en tu entorno: Establece una tradición familiar para expresar gratitud antes de las comidas o compartir lo que cada miembro de la familia está agradecido antes de dormir.\n6. Sé creativo con tu gratitud: Encuentra maneras creativas de mostrar tu agradecimiento, como manteniendo un diario de gratitud o capturando momentos que te generen gratitud en fotografías.'],

            "Pensamiento inverso": ['Por supuesto. Aquí está la explicación sobre cómo aplicar la técnica de pensamiento inverso.\n\nPensamiento saludable implica cambiar lo negativo por positivo. Ayuda a prevenir o controlar la depresión.\n\n1. Note y detenga sus pensamientos:\nEscucha tus pensamientos y lo que te dices refleja cómo te ves y puede ser positivo o negativo\n\n2. Pregúntese sobre sus pensamientos:\nEvalúa si tus pensamientos son buenos para ti y reconoce patrones negativos. Como por ejemplo:\n- Enfocarse en lo negativo: Ignorar lo bueno y centrarse solo en lo malo.\n- Debería hacer: Establecer expectativas rígidas sobre cómo deberíamos actuar.\n- Generalización exagerada: Tomar un ejemplo y aplicarlo a todas las situaciones.\n- Pensamiento "todo o nada": Ver todo en extremos, sin términos medios.\n\n3.Elija sus pensamientos: Escoge pensamientos útiles, registra los negativos y corrígelos diariamente.\n Así, tendrás pensamientos más acertados y positivos naturalmente.',
                                    '¡Claro! Aquí está la explicación sobre cómo aplicar la técnica del pensamiento inverso:\n\nAdoptar un pensamiento saludable significa transformar lo negativo en positivo, siendo beneficioso para prevenir o manejar la depresión.\n\n1. Reconoce y detén tus pensamientos:\nObserva tus pensamientos, ya que lo que te dices a ti mismo refleja tu percepción y puede ser tanto positivo como negativo.\n\n2. Cuestiona tus pensamientos:\nEvalúa si tus pensamientos te benefician y reconoce patrones negativos, tales como:\n- Centrarse en lo negativo: Pasar por alto lo positivo y concentrarse solo en lo negativo.\n- Expectativas rígidas: Establecer estándares estrictos sobre cómo deberíamos comportarnos.\n- Extrapolación excesiva: Tomar un caso específico y aplicarlo a todas las situaciones.\n- Pensamiento dicotómico: Ver todo en extremos, sin considerar términos intermedios.\n\n3. Selecciona tus pensamientos:\nOpta por pensamientos útiles, registra los negativos y corrígelos diariamente. De esta forma, cultivarás pensamientos más precisos y positivos de forma natural.',
                                    'Por supuesto. Aquí te presento la descripción de cómo emplear la técnica del pensamiento inverso:\n\nAdoptar una mentalidad positiva implica cambiar lo negativo por positivo, lo cual resulta beneficioso para prevenir o manejar la depresión.\n\n1. Observa y controla tus pensamientos:\nReconoce y detén tu corriente de pensamientos. Lo que te dices a ti mismo refleja tu percepción, pudiendo ser tanto positiva como negativa.\n\n2. Cuestiona tus pensamientos:\nEvalúa si tus pensamientos son beneficiosos y reconoce patrones negativos, como:\n- Enfoque en lo negativo: Ignorar lo positivo y concentrarse únicamente en lo negativo.\n- Imposiciones: Establecer expectativas estrictas sobre cómo deberíamos comportarnos.\n- Generalización excesiva: Tomar un caso específico y aplicarlo a todas las situaciones.\n- Pensamiento binario: Ver todo en extremos, sin considerar matices.\n\n3. Elige tus pensamientos:\nEscoge pensamientos útiles, registra los negativos y corrígelos diariamente. Así, cultivarás pensamientos más acertados y positivos de manera natural.'],

            "Visualización": ['Claro, ahora te explico, las de técnicas de visualización son herramientas que utilizan la imaginación para cambiar nuestros pensamientos y emociones, permitiéndonos dirigir nuestra mente hacia estados mentales positivos y placenteros.\n\n1. Cierra los ojos.\n2. Toma de 3 a 5 respiraciones abdominales profundas.\n3. Imagina un lugar especial al cual te encantaría ir, en el cual te sientas relajado.\n4. Cuando hayas elegido un lugar, imagínate allí. Gracias a la mente, puedes sentir que estás en ese lugar como si realmente estuviera sucediendo.\n5. Utiliza toda tu imaginación para enfocarte en los detalles que hacen que ese lugar y experiencia sean perfectos según tus deseos\n6. Sé consciente de lo cómodo que sientes el cuerpo cuando te imaginas en este lugar. Puedes notar que la respiración se vuelve más lenta y que sientes los músculos más relajados a medida que todo el cuerpo comienza a relajarse.',
                              'Por supuesto, las técnicas de visualización son herramientas que emplean la imaginación para influir positivamente en nuestros pensamientos y emociones, permitiéndonos enfocar la mente en estados mentales agradables y placenteros.\n\n1. Comienza cerrando los ojos.\n2. Realiza de 3 a 5 respiraciones profundas desde el abdomen.\n3. Elige un lugar especial que te haga sentir relajado y que te gustaría visitar en tu mente.\n4. Una vez que hayas seleccionado ese lugar, imagínate allí y siente como si estuvieras realmente allí.\n5. Utiliza toda tu imaginación para concentrarte en los detalles que hacen que ese lugar y experiencia sean perfectos según tus deseos.\n6. Observa cómo te sientes cómodo en tu cuerpo mientras te sumerges en esta visualización. Puedes notar que tu respiración se vuelve más pausada y que tus músculos se relajan gradualmente, llevando a una sensación de relajación en todo el cuerpo.',
                              'Ahora te explico, las técnicas de visualización son herramientas que utilizan la imaginación para influir positivamente en nuestros pensamientos y emociones, permitiéndonos enfocar la mente en estados mentales agradables y placenteros.\n\n1. Comienza cerrando los ojos.\n2. Lleva a cabo de 3 a 5 respiraciones profundas desde el abdomen.\n3. Selecciona un lugar especial que te proporcione relajación y que desees explorar en tu mente.\n4. Una vez que hayas elegido ese lugar, imagínate en él y experimenta la sensación de estar allí realmente.\n5. Utiliza toda tu capacidad imaginativa para detallar lo que hace que ese lugar y experiencia sean ideales según tus deseos.\n6. Observa cómo te sientes cómodo en tu cuerpo mientras te sumerges en esta visualización. Puedes notar que tu respiración se vuelve más pausada y que tus músculos se relajan gradualmente, lo que te lleva a experimentar una sensación de relajación en todo tu cuerpo.']

        }

        tecnicas = parameters.get('tecnicas', None)

        if tecnicas is not None and tecnicas[0] in respuestas4:
            categoria = tecnicas[0]
            respuesta_random = random.choice(respuestas4[categoria])
            fulfillment_text = respuesta_random
        else:
            fulfillment_text = "La palabra no coincide."

        # Crea la respuesta JSON
        response_data = {
            "fulfillmentText": fulfillment_text
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Lo siento pero no logré entenderte."})

def contacto_psicologa(parameters: dict, session_id: str):
    try:

        respuestas = ['Claro, estos son los datos para que puedas encontrar ayuda de un profesional capacitado:\n\n1. Puedes dirigirte al Departamento Psicologico del colegio:\n\n   - Este esta ubicado en el 3er Piso\n   - Su horario es de 7am - 6pm\n\nPuedes contarles lo que estas pasando a cualquiera de los internos o la Psicologa principal.\n\n!Ellos te brindaran la ayuda que necesites¡',
                      '''Por supuesto, aquí tienes la información para que encuentres apoyo de un profesional cualificado:\n\n1. Te recomendaría visitar el Departamento Psicológico de la escuela:\n\n   - Encuéntralos en el tercer piso.\n   - Están disponibles de 7 a.m. a 6 p.m.\n\nPuedes compartir tus experiencias con cualquiera de los internos o con la psicóloga principal. ¡Ellos estarán allí para proporcionarte la asistencia que necesitas!''',
                      '¡Claro! Aquí te dejo la información para que encuentres apoyo de un profesional capacitado:\n\n1. Dirígete al Departamento Psicológico de la escuela:\n\n   - Encuéntralos en el tercer piso.\n   - Están disponibles de 7 a.m. a 6 p.m.\n\nPuedes hablar con cualquiera de los internos o con la psicóloga principal sobre lo que estás pasando. ¡Ellos están ahí para ofrecerte la ayuda que necesitas!']

        respuesta_random = random.choice(respuestas)
        fulfillment_text = respuesta_random

        # Crea la respuesta JSON
        response_data = {
            "fulfillmentText": fulfillment_text
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Perdón no entendí la pregunta."})

def reproducir_video(parameters: dict, session_id: str):
    try:

        video_urls = {

            "ansiedad": ['https://github.com/JRsalinas98/video/assets/105223959/deb606f5-ada8-4ee6-a63a-c8ced5a593b8',
                         'https://github.com/JRsalinas98/video/assets/105223959/aa7a5127-cecf-4af6-abca-da576a7df6bc',
                         'https://github.com/JRsalinas98/video/assets/105223959/e0170c2d-68e0-4c93-a02e-bb0d23cd9d3d'
                         ],

            "depresión": ['https://github.com/JRsalinas98/video/assets/105223959/6b0d44f8-de81-4198-bb41-40bc3e70bcca',
                          'https://github.com/JRsalinas98/video/assets/105223959/1e1fecbe-44ba-4d6a-bb19-6b14a167d698',
                          'https://github.com/JRsalinas98/video/assets/105223959/f944afcd-56c9-408e-9d1e-f3534e4077ce']

        }

        condiciones = parameters.get('condiciones', None)

        if condiciones is not None and condiciones[0] in video_urls:
            categoria = condiciones[0]
            respuesta_random = random.choice(video_urls[categoria])
            video_url_final = respuesta_random

            fulfillment_text = "Aquí está el video que solicitaste."
        else:
            fulfillment_text = "La palabra no coincide."


        # Crea la respuesta JSON con la URL del video
        response_data = {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            fulfillment_text
                        ]
                    }
                },
                {
                    # Puedes agregar más bloques como este para más respuestas
                    "text": {
                        "text": [
                            video_url_final
                        ]
                    }
                }
            ]
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "Lo siento pero no logro entenderte."})

def abrir_cuestionarios(parameters: dict, session_id: str):
    try:

        cuestionario_tipo = {

            "ansiedad": ['El siguiente cuestionario te puede ayudar a saber si tienes ansiedad'],

            "depresión": ['El siguiente cuestionario te puede ayudar a saber si tienes depresion']

        }

        condiciones = parameters.get('condiciones', None)

        if condiciones is not None and condiciones[0] in cuestionario_tipo:
            categoria = condiciones[0]
            respuesta_random = random.choice(cuestionario_tipo[categoria])
            cuestionario_tipo_final = respuesta_random

            fulfillment_text = cuestionario_tipo_final
        else:
            fulfillment_text = "La palabra no coincide."


        # Crea la respuesta JSON con la URL del video
        response_data = {
            "fulfillmentText": fulfillment_text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            fulfillment_text
                        ]
                    }
                }
            ]
        }

        return JSONResponse(content=response_data)
    except Exception as e:
        return JSONResponse(content={"fulfillmentText": "No logré entenderte, mil disculpas."})