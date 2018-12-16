import struct
import os

s = struct.Struct(
    "I 20s I"
)  # essa é minha struct (I = inteiro, 20s = string de 20 char)
obj_tam = s.size

# Constantes
MAXNARQS = 100
MAXMEM = 84
NUM_FILES = MAXNARQS/2

# Variáveis globais
max_reg = 0

# função definida pois o valor do atributo nome é preenchido automaticamente para ter 20 caracteres
# dessa forma, pego apenas o nome para a impressão


def fixName(nome):
    a = ""
    idx = 0
    while idx < 20 and nome[idx] != "\x00":
        a = a + nome[idx]
        idx += 1
    return a


def calcConfig():
    global MAXNARQS, MAXMEM, obj_tam, max_reg
    max_reg = int(MAXMEM/obj_tam)
    # num_files = max_reg*2 if max_reg*2 <= MAXNARQS else MAXNARQS


def getObjectFromString(line):
    data = []
    for i in range(0, 3):
        aux = line.find(" ")
        data.append(line[:aux] if aux != -1 else line)
        line = line[aux+1:]
    reg = s.pack(int(data[0]), data[1].encode("utf-8"), int(data[2]))
    return reg


def getStringFromObject(reg):
    reg = s.unpack(reg)
    return "{} {} {}".format(reg[0], fixName(reg[1].decode("utf-8")), reg[2])


def readLine():
    with open("entrada.dat", "r") as file:
        reg = getObjectFromString(file.readline())
        return reg


def createRuns():
    with open("entrada.dat", "r") as file:
        tmpCount = 0
        count = 0
        for line in file:
            if os.path.exists('./tmp' + str(tmpCount)) == False:
                open('./tmp' + str(tmpCount), 'w').close()
            if (count == max_reg):
                count = 0
                tmpCount += 1
            insertLine('./tmp' + str(tmpCount), line + "\n")
            count+=1


def insertLine(file, reg):
    with open(file, "a") as file:
        file.write(reg)


calcConfig()
createRuns()
# reg = readLine()
