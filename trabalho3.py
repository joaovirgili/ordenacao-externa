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

### Implementação do QuickSort ###
def quicksort(v, p , r): #recebe uma run para ordenar
    if p < r:
        q = particionar(v, p, r)
        quicksort(v, p, q-1) #metade a esquerda da run (onde os elementos são menores que o vetor)
        quicksort(v, q+1, r) #metade a direita da run (onde os elementos são maiores que o vetor)
def particionar(v, p, r):
    x = v[p][0]
    i = p
    j = p + 1

    while  j<= r: #percorre o vetor
        if v[j][0] < x:
            i += 1 #incrementa se um numero for maior que o pivo
            trocar(v, i, j) #troca o lugar do i com o j
        j +=1
    trocar(v, p, i)

    return i
def trocar(v, m, n):
    temp = v[n]
    v[n] = v[m]
    v[m] = temp
### --- ###

def calcConfig():
    global MAXNARQS, MAXMEM, obj_tam, max_reg
    max_reg = int(MAXMEM/obj_tam)

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

def insertLine(file, reg):
    with open(file, "a") as file:
        file.write(reg+"\n")

def sortRegisters(arr):
    quicksort(arr, 0, len(arr)-1)

def insertObjects(file, arr):
    for elem in arr:
        insertLine(file, "{} {} {}".format(elem[0], fixName(elem[1].decode("utf-8")), elem[2]))

# Este método percorrerá o arquivo e criará as runs em cada arquivo temporário.
def createRuns():
    with open("entrada.dat", "r") as file:
        tmpCount = 0
        count = 0
        data = []
        for line in file:
            path = './tmp' + str(tmpCount)
            if os.path.exists(path) == False:
                open(path, 'w').close()
            if (count == max_reg): # limite de registro carregado na memória principal
                sortRegisters(data) # data será ordenado
                insertObjects(path, data) # insere a run no arquivo temporário
                count = 0
                tmpCount = 0 if tmpCount == NUM_FILES else tmpCount+1
                data = []

            data.append(s.unpack(getObjectFromString(line.rstrip("\n"))))
            count+=1
        if count != 0: # caso o número de registro não exceda o tamanho máximo
            path = './tmp' + str(tmpCount)
            sortRegisters(data) # data será ordenado
            insertObjects(path, data) # insere a run no arquivo temporário





calcConfig()
createRuns()
# a = [5,9,1,7,2,9,1,4,6,2,57,2]
# quicksort(a, 0, len(a)-1)
# print(a)

# reg = readLine()
