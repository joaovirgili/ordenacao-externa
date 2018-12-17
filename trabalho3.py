import struct
import os

s = struct.Struct(
    "I 20s I"
)  # essa é minha struct (I = inteiro, 20s = string de 20 char)
obj_tam = s.size

# Constantes
MAXNARQS = 100
MAXMEM = 56
TMP_PATH = './tmp'

# Variáveis globais
max_reg = 0 # Número máximo de arquivos na memória principal
num_files = 0 # Número de arquivos
actual_read_file = 1 # Arquivo atual para começar a ser lido para fazer o merge
tmp_to_write = 0 # Primeiro arquivo vazio
num_reg = 0

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
    max_reg = int(MAXMEM/obj_tam) if (int(MAXMEM/obj_tam) <= 50) else 50


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
    global num_files, actual_read_file, tmp_to_write, num_reg
    with open("entrada.dat", "r") as file:
        tmpCount = 0 # Contador de arquivos temporários
        count = 0 # Contador de registros na memória principal 
        data = [] # Registros na memória principal
        for line in file:
            num_reg += 1
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
        tmp_to_write = num_files+1
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

# Método retornará se deve ainda fazer merge ou não
def stillMerge(registers_idx):
    global tmp_to_write
    for i in range (0, len(registers_idx)):
        elem = registers_idx[i]
        line = readLine(TMP_PATH + str(actual_read_file + i) ,elem)
        if (line != None):
            tmp_to_write += 1
            return True
    return False

def eliminateFile(path):
    with open(path, "w") as file:
        file.writelines([])

def eliminateTmpFiles():
    global actual_read_file, max_reg, tmp_to_write, num_files
    tmp_to_write = actual_read_file
    for i in range (0,max_reg):
        path = TMP_PATH + str(actual_read_file)
        eliminateFile(path)
        actual_read_file += 1
    if (actual_read_file > num_files):
        actual_read_file = 1

def finished():
    global num_files
    count = 0
    file = 0
    for i in range (0, num_files):
        path = TMP_PATH + str(i + 1)
        line  = readLine(path, 0)
        if (line != None):
            count += 1
            file = i + 1
    if (count == 1):
        return [True, file]
    else:
        return False

def finish(file):
    with open("saida.dat", 'w') as saida:
        with open(TMP_PATH + str(file), "r+") as file:
            for i, line in enumerate(file):
                if (i == num_reg - 1):
                    line = line[:len(line)-2]
                saida.write(line)

    for i in range (0, num_files):
        with open(TMP_PATH + str(i + 1)) as file:
            file.close()
        os.remove(TMP_PATH + str(i + 1))
                

def merge(registers_idx):
    global num_files, TMP_PATH, actual_read_file, tmp_to_write
    reg_in_mem = max_reg
    nextRegister = []
    registers = []
    registers_runs = [] # array para referenciar o final da run (se True, run finalizada)
    if (len(registers_idx) == 0):
        for i in range(max_reg):
            registers_idx.append(0)
    for i in range(max_reg): # inicia todos como false
        registers_runs.append(False)

    for i in range(0, max_reg): 
        if (registers_runs[i] == False): # Posso ler
            response = readLine(TMP_PATH + str(actual_read_file+i), registers_idx[0])
            if (response == None):
                registers_runs[i] = True
                registers.append(None)
                reg_in_mem -= 1
            else:
                reg = response[0]
                registers_runs[i] = response[1]
                registers.append(reg)

    while (reg_in_mem > 0):
        if (len(nextRegister) > 0 and nextRegister[1] == True):
                registers_runs[response[0]] = True
        # Pega o menor dos registros na memória principal
        response = getLowestId(registers)
        fromFile = TMP_PATH + str(response[0]+actual_read_file)
        toFile = TMP_PATH + str(tmp_to_write)
        registerObj = response[1]

        # Insere o registro no novo arquivo temporario
        reg_insert = getStringFromObject(registerObj)
        if (registers_runs[response[0]] == True and reg_in_mem == 1):
            reg_insert += '.'
        insertObject(fromFile, toFile, reg_insert)
        # Remove o registro da memória principal
        registers.remove(response[1])
        # Atualiza o próximo index a ser lido
        registers_idx[response[0]] += 1
        # Pega o proximo registro no arquivo que foi retirado e guarda na memória principal
        # Caso a run esteja finalizada, marca como None
        if (registers_runs[response[0]] == True):
            registers.insert(response[0], None)
            reg_in_mem -= 1
        else:
            nextRegister = readLine(fromFile, registers_idx[response[0]])
            registers.insert(response[0], nextRegister[0])
    
    if (stillMerge(registers_idx)):
        merge(registers_idx)
    else:
        eliminateTmpFiles()
        response = finished()
        if (response == False):
            merge([])
        # else:
        #     finish(response[1])
           
calcConfig()
createRuns()
merge([])
