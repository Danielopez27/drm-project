# Prototipo DRM educativo con FastAPI y Godot

Este proyecto implementa una demo educativa de DRM para la materia de Introducción a la Criptografía y Seguridad de la Información.

## Idea general

El cliente Godot lee un archivo crítico (`critical.gd`), calcula su hash SHA-256 y lo envía a un servidor FastAPI.  
El servidor compara ese hash con un valor esperado. Si coincide, entrega una llave. Si no coincide, deniega el acceso.

## Flujo actual

```text
Godot inicia
↓
Lee scripts/critical.gd
↓
Calcula SHA-256
↓
POST /verify al servidor FastAPI
↓
Servidor valida el hash
↓
Si es correcto, entrega key
↓
Godot desbloquea contenido protegido