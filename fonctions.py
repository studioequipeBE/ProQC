def tcActuel(num_image: int, starttc: str, framerate: int = 24) -> str:
    """
    Donne le TC actuel à l'aide d'un nombre d'images et sur base d'un tc de départ.

    :param int num_image: Numéro d'image.
    :param str starttc: Timecode début.q
    :param int framerate: Framerate.
    """
    import timecode as Timecode
    import TimecodeP as tc

    tc1 = Timecode(framerate, starttc)
    if num_image > 0:
        # Comme le résultat est toujours une image en trop, j'enlève ce qu'il faut : :)
        tc2 = Timecode(framerate, tc.frames_to_timecode((num_image - 1), framerate))
        tc3 = tc1 + tc2
        return tc3
    else:
        return tc1


def startTimeCodeFile(ffmpeg: str, fichier: str) -> str:
    """
    Timecode du fichier analyse.

    :param str ffmpeg: Où se trouve FFMPEG !
    :param str fichier: Le fichier.
    """
    import subprocess as sp

    command = [ffmpeg, '-i', fichier]
    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    pipe.stdout.readline()
    pipe.terminate()
    infos = str(pipe.stderr.read())
    tc = ''

    index = infos.find('timecode')

    for i in range(18, 29):
        tc += infos[index + i]
    return tc


def licence() -> bool:
    """
    Si on peut utiliser le programme.
    """
    import ServeurDate as date

    # Se connecte pour voir si on dépasse la limite d'utilisation du programme :
    if int(date.aujourdhui()) <= 20230101:
        print('Licence OK')
        return True
    else:
        print('Licence depassee/!\\')
        return False


def getFFmpeg() -> str:
    """
    Récupère le chemin de FFmpeg.
    """
    import platform
    import os

    chemin_ffmpeg = os.getcwd() + os.sep + 'modules' + os.sep
    match platform.system():
        case 'Windows':
            chemin_ffmpeg += 'ffmpeg.exe'
        case 'macOS':
            chemin_ffmpeg += 'ffmpeg'

    return chemin_ffmpeg
