import struct
import os

s = struct.Struct(
    "I 20s I"
)  # essa é minha struct (I = inteiro, 20s = string de 20 char)
obj_tam = s.size
print(obj_tam)

# Constantes
MAXNARQS = 100
MAXMEM = 84
TMP_PATH = './tmp'

# Variáveis globais
max_reg = 0 # Número máximo de arquivos na memória principal
num_files = 0 # Número de arquivos
actual_read_file = 1 # Arquivo atual para começar a ser lido para fazer o merge
first_blank_tmp = 0 # Primeiro arquivo vazio

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
    last = False
    for i in range(0, 3):
        aux = line.find(" ")
        data.append(line[:aux] if aux != -1 else line)
        line = line[aux+1:]
    if (data[2][len(data[2])-1:] == '.'): # checa se é o último da run
        data[2] = data[2][:len(data[2])-1]
        last = True
    reg = s.pack(int(data[0]), data[1].encode("utf-8"), int(data[2]))
    return [reg, last]

def getStringFromObject(reg):
    reg = s.unpack(reg)
    return "{} {} {}".format(reg[0], fixName(reg[1].decode("utf-8")), reg[2])

def readNextLine(file):
    with open(file, "r") as file:
        line = file.readline()
        reg = getObjectFromString(line.rstrip("\n"))
        return reg

def readLine(file, idx):
    with open(file, "r") as file:
        for i, line in enumerate(file):
            if (i == idx):
                return getObjectFromString(line.rstrip("\n"))
            

def insertLine(file, reg):
    with open(file, "a") as file:
        file.write(reg+"\n")

def sortRegisters(arr):
    quicksort(arr, 0, len(arr)-1)

def insertObjects(file, arr):
    for i in range (0, len(arr)):
        elem = arr[i]
        line = "{} {} {}." if (i == len(arr) - 1) else "{} {} {}" # o ponto determina o final da run
        insertLine(file, line.format(elem[0], fixName(elem[1].decode("utf-8")), elem[2]))

def insertObject(fromFile, toFile, reg): # TODO: checar a marcação do último arquivo da run
    with open(toFile, "a") as file:
        file.write(reg+"\n")

# Este método percorrerá o arquivo e criará as runs em cada arquivo temporário.
def createRuns():
    global num_files, actual_read_file, first_blank_tmp
    with open("entrada.dat", "r") as file:
        tmpCount = 0 # Contador de arquivos temporários
        count = 0 # Contador de registros na memória principal 
        data = [] # Registros na memória principal
        for line in file:
            # Crio o arquivo temporário, caso não exista
            path = TMP_PATH + str(tmpCount+1)
            if os.path.exists(path) == False:
                open(path, 'w').close()
                num_files += 1
            
            # Adiciono a linha lida do arquivo na memoria principal
            data.append(s.unpack(getObjectFromString(line.rstrip("\n"))[0]))
            count += 1

            # Caso a memória tenha estourado, faço a ordenação e a inserção no arquivo temporário
            if (count == max_reg): # limite de registro carregado na memória principal
                sortRegisters(data) # data será ordenado
                insertObjects(path, data) # insere a run no arquivo temporário
                count = 0
                tmpCount = 0 if tmpCount+1 == max_reg else tmpCount+1 
                data = []

        if count != 0: # caso o número de registro não exceda o tamanho máximo
            path = TMP_PATH + str(tmpCount+1)
            sortRegisters(data) 
            insertObjects(path, data)
        
        aux = num_files
        first_blank_tmp = num_files+1
        for i in range (0, aux):
            num_files += 1
            path = TMP_PATH + str(num_files)
            if os.path.exists(path) == False:
                open(path, 'w').close()

# função que retorna o menor dos registros e de qual arquivo ele veio
def getLowestId(registers):
    idx = 0
    while (registers[idx] == None):
        idx += 1
    menorObj = registers[idx]
    menorID = s.unpack(registers[idx])[0]
    for i in range(0,len(registers)):
        if (registers[i] != None):
            actualID = s.unpack(registers[i])[0]
            if (actualID < menorID):
                menorObj = registers[i]
                menorID = actualID
                idx = i
    return [idx, menorObj]

def merge():
    #TODO:
    # Pegar o primeiro registro de cada fita
    # Verficiar o menor entre eles e inserir no novo arquivo temporário
    global num_files, TMP_PATH, actual_read_file
    nextRegister = []
    file_reading = actual_read_file
    registers = []
    registers_idx = [] # linha a ser lida no arquivo
    registers_runs = [] # array para referenciar o final da run (se True, run finalizada)
    for i in range(max_reg): # inicia todos como false
        registers_runs.append(False)
        registers_idx.append(0)

    for i in range(0, max_reg): 
        if (registers_runs[i] == False): # Posso ler
            response = readNextLine(TMP_PATH + str(actual_read_file+i))
            reg = response[0]
            registers_runs[i] = response[1]
            registers.append(reg)

    while ((False in registers_runs) == True):

        if (len(nextRegister) > 0 and nextRegister[1] == True):
                registers_runs[response[0]] = True

        # Pega o menor dos registros na memória principal
        response = getLowestId(registers)
        fromFile = TMP_PATH + str(response[0]+actual_read_file)
        toFile = TMP_PATH + str(first_blank_tmp)
        registerObj = response[1]

        # Insere o registro no novo arquivo temporario
        insertObject(fromFile, toFile, getStringFromObject(registerObj))
        # Remove o registro da memória principal
        registers.remove(response[1])
        if (registers_runs[response[0]] == True):
            registers.insert(response[0], None)
        # Atualiza o index a ser lido
        registers_idx[response[0]] += 1
        # Pega o proximo registro no arquivo que foi retirado e guarda na memória principal
        if (registers_runs[response[0]] == True):
            print("acabou run")
            # while (registers_runs[response[0]] == True):
            #     file_reading += 1
                # fromFile = TMP_PATH + str(response[0]+actual_read_file)
        else:
            nextRegister = readLine(fromFile, registers_idx[response[0]])
            registers.insert(response[0], nextRegister[0])
            
    
    
    



calcConfig()
createRuns()
merge()
# print(readLine('entrada.dat', 3))