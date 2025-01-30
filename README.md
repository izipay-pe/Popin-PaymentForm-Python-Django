<p align="center">
  <img src="https://github.com/izipay-pe/Imagenes/blob/main/logos_izipay/logo-izipay-banner-1140x100.png?raw=true" alt="Formulario" width=100%/>
</p>

# Popin-PaymentForm-Python-Django

## Índice

➡️ [1. Introducción](#-1-introducci%C3%B3n)  
🔑 [2. Requisitos previos](#-2-requisitos-previos)  
🚀 [3. Ejecutar ejemplo](#-3-ejecutar-ejemplo)  
🔗 [4. Pasos de integración](#4-pasos-de-integraci%C3%B3n)  
💻 [4.1. Desplegar pasarela](#41-desplegar-pasarela)  
💳 [4.2. Analizar resultado de pago](#42-analizar-resultado-del-pago)  
📡 [4.3. Pase a producción](#43pase-a-producci%C3%B3n)  
🎨 [5. Personalización](#-5-personalizaci%C3%B3n)  
📚 [6. Consideraciones](#-6-consideraciones)

## ➡️ 1. Introducción

En este manual podrás encontrar una guía paso a paso para configurar un proyecto de **[Python-Django]** con la pasarela de pagos de IZIPAY. Te proporcionaremos instrucciones detalladas y credenciales de prueba para la instalación y configuración del proyecto, permitiéndote trabajar y experimentar de manera segura en tu propio entorno local.
Este manual está diseñado para ayudarte a comprender el flujo de la integración de la pasarela para ayudarte a aprovechar al máximo tu proyecto y facilitar tu experiencia de desarrollo.

> [!IMPORTANT]
> En la última actualización se agregaron los campos: **nombre del tarjetahabiente** y **correo electrónico** (Este último campo se visualizará solo si el dato no se envía en la creación del formtoken). 

<p align="center">
  <img src="https://github.com/izipay-pe/Imagenes/blob/main/formulario_popin/Imagen-Formulario-Popin.png?raw=true" alt="Formulario" width="350"/>
</p>

## 🔑 2. Requisitos Previos

- Comprender el flujo de comunicación de la pasarela. [Información Aquí](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/guide/start.html)
- Extraer credenciales del Back Office Vendedor. [Guía Aquí](https://github.com/izipay-pe/obtener-credenciales-de-conexion)
- Para este proyecto utilizamos Python 3.12
- Para este proyecto utilizamos la herramienta Visual Studio Code.
> [!NOTE]
> Tener en cuenta que, para que el desarrollo de tu proyecto, eres libre de emplear tus herramientas preferidas.

## 🚀 3. Ejecutar ejemplo


### Clonar el proyecto
```sh
git clone https://github.com/izipay-pe/Popin-PaymentForm-Python-Django.git
``` 

### Datos de conexión 

Reemplace **[CHANGE_ME]** con sus credenciales de `API REST` extraídas desde el Back Office Vendedor, revisar [Requisitos previos](#-2-requisitos-previos).

- Editar el archivo `keys.py` en la ruta `./Keys/keys.py`:
```python
keys = {
  # Identificador de su tienda
  "USERNAME": "~ CHANGE_ME_USER_ID ~",

  # Clave de Test o Producción
  "PASSWORD": "~ CHANGE_ME_PASSWORD ~",

  # Clave Pública de Test o Producción
  "PUBLIC_KEY": "~ CHANGE_ME_PUBLIC_KEY ~",

  # Clave HMAC-SHA-256 de Test o Producción
  "HMACSHA256": "~ CHANGE_ME_HMAC_SHA_256 ~"
}
```

### Ejecutar proyecto

1. Abre la terminar y ejecuta los siguientes comandos para crear y activar un entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

2.  Instala las librerías y paquetes necesarios definidos en `requirements.txt`:
```bash
pip install -r requirements.txt
```

3. Realiza las migraciones para aplicar los cambios en la base de datos:
```bash
python manage.py migrate
```
4. Ejecuta el proyecto:
```bash
python manage.py runserver
```
5. Podrás acceder a través de `http://127.0.0.1:8000/`

## 🔗4. Pasos de integración

<p align="center">
  <img src="https://i.postimg.cc/pT6SRjxZ/3-pasos.png" alt="Formulario" />
</p>

## 💻4.1. Desplegar pasarela
### Autentificación
Extraer las claves de `usuario` y `contraseña` del Backoffice Vendedor, concatenar `usuario:contraseña` y agregarlo en la solicitud del encabezado `Authorization`. Podrás encontrarlo en el archivo `./Demo/views.py`.
```python
#Encabezado Basic con concatenación de "usuario:contraseña" en base64
auth = 'Basic ' + base64.b64encode(f"{keys["USERNAME"]}:{keys["PASSWORD"]}".encode('utf-8')).decode('utf-8')

headers = {
    'Content-Type': 'application/json',
    'Authorization': auth,
}
```
ℹ️ Para más información: [Autentificación](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/guide/embedded/keys.html)
### Crear formtoken
Para configurar la pasarela se necesita generar un formtoken. Se realizará una solicitud API REST a la api de creación de pagos:  `https://api.micuentaweb.pe/api-payment/V4/Charge/CreatePayment` con los datos de la compra para generar el formtoken. Podrás encontrarlo en el archivo `./Demo/views.py`.

```python
def checkout(request):
    url = 'https://api.micuentaweb.pe/api-payment/V4/Charge/CreatePayment'

    auth = 'Basic ' + base64.b64encode(f"{keys["USERNAME"]}:{keys["PASSWORD"]}".encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth,
    }

    data = {
        "amount": int(float(request.POST['amount']) * 100),
        "currency": request.POST['currency'],
        "orderId": request.POST['orderId'],
        "customer": {
            "email": request.POST['email'],
            "firstName": request.POST['firstName'],
            ..
            ..
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status'] != 'SUCCESS':
        raise Exception
    
    token = response_data['answer']['formToken']
    return render(request, 'Demo/checkout.html', {'token': token, 'publickey': keys['PUBLIC_KEY']})
```
ℹ️ Para más información: [Formtoken](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/guide/embedded/formToken.html)

### Visualizar formulario
Para desplegar la pasarela, se configura la llave `public key` en el encabezado (Header) del archivo `./templates/Demo/checkout.html`. En el ejemplo la llave se extrae directamente del archivo `keys/keys.py`.

Header: 
Se coloca el script de la libreria necesaria para importar las funciones y clases principales de la pasarela.
```javascript
<script type="text/javascript"
  src="https://static.micuentaweb.pe/static/js/krypton-client/V4.0/stable/kr-payment-form.min.js"
  kr-public-key="{{ publickey }}"
  kr-post-url-success="result" kr-language="es-Es">
</script>

<!-- Estilos de la pasarela de pagos -->
<link rel="stylesheet" href="https://static.micuentaweb.pe/static/js/krypton-client/V4.0/ext/classic.css">
<script type="text/javascript" src="https://static.micuentaweb.pe/static/js/krypton-client/V4.0/ext/classic.js">
</script>
```
Además, se inserta en el body una etiqueta div con la clase `kr-embedded` que deberá tener el atributo `kr-form-token` e incrustarle el `formtoken` generado en la etapa anterior.

Body:
```javascript
<div id="micuentawebstd_rest_wrapper">
    <div class="kr-embedded" kr-popin kr-form-token="<%= formToken %>"></div>
</div>
```
ℹ️ Para más información: [Visualizar formulario](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/guide/embedded/formToken.html)

## 💳4.2. Analizar resultado del pago

### Validación de firma
Se configura la función `checkHash` que realizará la validación de los datos recibidos por el servidor luego de realizar el pago mediante el parámetro `kr-answer` utilizando una clave de encriptación definida en `key`. Podrás encontrarlo en el archivo `./Demo/views.py`.

```python
def checkHash(response, key):

    answer = response['kr-answer'].encode('utf-8')

    calculateHash = hmac.new(key.encode('utf-8'), answer, hashlib.sha256).hexdigest()

    return calculateHash == response['kr-hash']
```

Se valida que la firma recibida es correcta. Para la validación de los datos recibidos a través de la pasarela de pagos (front) se utiliza la clave `HMACSHA256`.

```python
#Validación de firma
if not checkHash(request.POST, keys["HMACSHA256"]) : 
    raise Exception("Invalid signature")
```
En caso que la validación sea exitosa, se puede extraer los datos de `kr-answer` a través de un JSON y mostrar los datos del pago realizado.

```python
answer_json = json.loads(request.POST['kr-answer'])
```
ℹ️ Para más información: [Analizar resultado del pago](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/kb/payment_done.html)

### IPN
La IPN es una notificación de servidor a servidor (servidor de Izipay hacia el servidor del comercio) que facilita información en tiempo real y de manera automática cuando se produce un evento, por ejemplo, al registrar una transacción.

Se realiza la verificación de la firma utilizando la función `checkHash`. Para la validación de los datos recibidos a través de la IPN (back) se utiliza la clave `PASSWORD`. Se devuelve al servidor de izipay un mensaje confirmando el estado del pago.

Se recomienda verificar el parámetro `orderStatus` para determinar si su valor es `PAID` o `UNPAID`. De esta manera verificar si el pago se ha realizado con éxito.

Podrás encontrarlo en el archivo `./Demo/views.py`.

```python
@csrf_exempt
def ipn(request):
    if not request.POST: 
        raise Exception("No post data received!")

    #Validación de firma en IPN
    if not checkHash(request.POST, keys["PASSWORD"]) : 
        raise Exception("Invalid signature")
    
    answer = json.loads(request.POST['kr-answer']) 
    transaction = answer['transactions'][0]

    #Verificar orderStatus: PAID / UNPAID
    orderStatus = answer['orderStatus']
    orderId = answer['orderDetails']['orderId']
    transactionUuid = transaction['uuid']

    return HttpResponse(status=200, content=f"OK! OrderStatus is {orderStatus} ")
```

La ruta o enlace de la IPN debe ir configurada en el Backoffice Vendedor, en `Configuración -> Reglas de notificación -> URL de notificación al final del pago`

<p align="center">
  <img src="https://i.postimg.cc/XNGt9tyt/ipn.png" alt="Formulario" width=80%/>
</p>

ℹ️ Para más información: [Analizar IPN](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/api/kb/ipn_usage.html)

### Transacción de prueba

Antes de poner en marcha su pasarela de pago en un entorno de producción, es esencial realizar pruebas para garantizar su correcto funcionamiento.

Puede intentar realizar una transacción utilizando una tarjeta de prueba con la barra de herramientas de depuración (en la parte inferior de la página).

<p align="center">
  <img src="https://i.postimg.cc/3xXChGp2/tarjetas-prueba.png" alt="Formulario"/>
</p>

- También puede encontrar tarjetas de prueba en el siguiente enlace. [Tarjetas de prueba](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/api/kb/test_cards.html)

## 📡4.3.Pase a producción

Reemplace **[CHANGE_ME]** con sus credenciales de PRODUCCIÓN de `API REST` extraídas desde el Back Office Vendedor, revisar [Requisitos Previos](#-2-requisitos-previos).

- Editar el archivo `keys.py` en la ruta `./Keys/keys.py`:
```python
keys = {
  # Identificador de su tienda
  "USERNAME": "~ CHANGE_ME_USER_ID ~",

  # Clave de Test o Producción
  "PASSWORD": "~ CHANGE_ME_PASSWORD ~",

  # Clave Pública de Test o Producción
  "PUBLIC_KEY": "~ CHANGE_ME_PUBLIC_KEY ~",

  # Clave HMAC-SHA-256 de Test o Producción
  "HMACSHA256": "~ CHANGE_ME_HMAC_SHA_256 ~"
}
```

## 🎨 5. Personalización

Si deseas aplicar cambios específicos en la apariencia de la pasarela de pago, puedes lograrlo mediante la modificación de código CSS. En este enlace [Código CSS - Popin](https://github.com/izipay-pe/Personalizacion/blob/main/Formulario%20Popin/Style-Personalization-PopIn.css) podrá encontrar nuestro script para un formulario popin.

<p align="center">
  <img src="https://github.com/izipay-pe/Imagenes/blob/main/formulario_popin/Imagen-Formulario-Custom-Popin.png?raw=true" alt="Formulario Popin"/>
</p>

## 📚 6. Consideraciones

Para obtener más información, echa un vistazo a:

- [Formulario incrustado: prueba rápida](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/quick_start_js.html)
- [Primeros pasos: pago simple](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/javascript/guide/start.html)
- [Servicios web - referencia de la API REST](https://secure.micuentaweb.pe/doc/es-PE/rest/V4.0/api/reference.html)
