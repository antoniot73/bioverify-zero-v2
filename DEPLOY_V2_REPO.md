# Despliegue BioVerify-Zero v2

Nuevo repositorio GitHub:

```text
https://github.com/antoniot73/bioverify-zero-v2
```

## Configurar remoto GitHub

Desde la carpeta del proyecto:

```powershell
git remote -v
git remote set-url origin https://github.com/antoniot73/bioverify-zero-v2.git
```

Si no existe `origin`:

```powershell
git remote add origin https://github.com/antoniot73/bioverify-zero-v2.git
```

## Subir a GitHub

```powershell
git add .
git commit -m "feat: implement BioVerify-Zero v2 face embedding demo"
git branch -M main
git push -u origin main
```

## Hugging Face Space

Si el Space público seguirá siendo el mismo:

```powershell
git remote add hf git@hf.co:spaces/antoniot73/bioverify-zero
git push hf main
```

Si vas a crear un Space nuevo para v2, cambia el remoto `hf` por la URL SSH del nuevo Space.
