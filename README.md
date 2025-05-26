# ListSerial

ListSerial es una utilidad en Python para listar los puertos seriales disponibles en el sistema, mostrando su nombre y descripción (cuando está disponible).

## Instalación

1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias necesarias ejecutando:

```bash
# UV tool is required
$ uv tool install -U .
```

## Uso

Puedes ejecutar el script principal para mostrar los puertos seriales disponibles:

```bash
$ listserial
```

La salida mostrará una lista de puertos seriales detectados, por ejemplo:

```
Available serial ports:

* COM3 - USB Serial Device
* COM4 - Arduino Uno
```

Si no hay puertos disponibles, verás:

```
No serial port is being used
```

## Compatibilidad

- Windows
- Linux
- macOS

## Créditos

Inspirado por:  
<https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python>
