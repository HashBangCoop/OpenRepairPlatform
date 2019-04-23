from django.core.exceptions import ValidationError

MAX_SIZE_MB = 1


def validate_image(image):
    file_size = image.file.size
    if file_size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"La taille maximale d'une image est de " f"{MAX_SIZE_MB}MB"
        )
