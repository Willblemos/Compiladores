#funcao auxiliar para eliminar espacos no comeco e fim de uma string
SPACES = [' ', '\n', '\t']
funTable = {}
varsNumber = 0
varTable = {}
stack = []
scope = 0
currentName = ''
currentFun = []
currentParameters = []
currentVar = ''
outputText = ['']
semanticErrors = []

def trim(txt, line, column):
    i = 0
    l = line
    c = column
    while i < len(txt) and txt[i] in SPACES:
        c += 1
        if txt[i] == '\n':
            l += 1
            c = 0
        i += 1
    j = len(txt) - 1
    if i <= j:
        return [txt[i: j + 1], l, c]
    return ['', l, c]

def isLetter(s):
    return s >= 'a' and s <= 'z'

def getLastStack():
    if len(stack) == 0:
        return '0'
    return stack[-1]

#baseado na derivacao de <Program> se faz uma funcao
def program(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 2 and txt[0:2] == 'if' and not isLetter(txt[2]): #caso if
        outputText[-1] += ('\t' * len(stack)) + 'if ('
        result = exp(txt[2:], l, c + 2)
        outputText[-1] += ') != 0:\n'
        if not result[0]:
            return result
        trimmed = trim(result[1], result[2], result[3])
        txt = trimmed[0]
        l = trimmed[1]
        c = trimmed[2]
        if len(txt) >= 4 and txt[0:4] == 'then': #precisa then
            scope += 1
            stack.append(getLastStack() + '-' + str(scope))
            outputText.append('')#adiciona uma linha para o codigo dentro do if
            result = program(txt[4:], l, c + 4)
            if not result[0]:
                return result
            res = outputText.pop()#recupera o codigo dentro do if
            outputText[-1] += res
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) >= 4 and txt[:4] == 'else': #caso else
                stack.pop()
                outputText[-1] += '\n' + ('\t' * len(stack)) + 'else:\n'                
                scope += 1
                stack.append(getLastStack() + '-' + str(scope))                
                outputText.append('')#adiciona uma linha para o codigo dentro do else
                result = program(txt[4:], l, c + 4)
                if not result[0]:
                    return result
                res = outputText.pop()#recupera o codigo dentro do else
                outputText[-1] += res
                trimmed = trim(result[1], result[2], result[3])
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
            stack.pop()
            return [True, txt, l, c]
        return [False, txt, l, c, 'Missing "then"!']#caso nao tenha o then apos o if
    elif len(txt) > 0 and isLetter(txt[0]) and not (len(txt) > 4 and txt[:4] == 'else' and not isLetter(txt[4])):#caso seja algo comecando por a ou z
        currentName = txt[0]#comeca ler um identificador
        result = barId(txt[1:], l, c + 4)
        if not result[0]:
            return result
        result = posId(result[1], result[2], result[3])
        if not result[0]:
            return result
        return program(result[1], result[2], result[3])
    return [True, txt, l, c] #caso vazio

#baseado na derivacao de <Id(com barra)> se faz uma funcao
def barId(txt, l, c):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    if len(txt) > 0 and isLetter(txt[0]):#caso comece com uma letra
        currentName += txt[0]#apenda cada caracter ao identificador lido
        return barId(txt[1:], l, c + 1)
    return [True, txt, l, c] #caso vazio

#baseado na derivacao de <Pos Id> se faz uma funcao
def posId(txt_original, line, column):
    global varsNumber, varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] == '=':#caso comeca com igual, atribuicao de variavel
            currentVar = currentName#o identificador lido e a variavel que sera atribuida
            varNumber = varsNumber
            varsNumber += 1
            outputText[-1] += ('\t' * len(stack)) + 'v' + str(varNumber) + ' = '#coloca na saida a variavel =
            if currentVar not in varTable:#mapeia a variavel na tabela de simbolos
                varTable.update({currentVar :[]})
            result = exp(txt[1:], l, c + 1)#obtem a expressao atribuida a variavel
            varTable[currentVar].append([getLastStack(), varNumber])#associa o escopo (faz depois para evitar que seja usada na expressao dela caso seja a primeira vez que aparece)
            outputText[-1] += '\n'#troca a linha
            return result
        elif txt[0] == '(':#caso comeca com parentesis aberto, chamado ou atribuicao de funcao
            currentFun.append(currentName)#na pilha das funcoes abertas adiciona a atual
            currentParameters.append(0)#adiciona no topo da pilha dos parametros abertos o valor deles
            outputText.append('')#adiciona um elemento na pilha de saida para escrever o primeiro parametro se houver
            if currentFun[-1] not in funTable:
                funTable.update({currentFun[-1]: []})#se a funcao nao estiver mapeada, criar uma entrada vazia para ela
            return fun(txt[1:], l, c + 1)
    return [False, txt, l, c, 'Invalid command: expected an attribution a function definition or a function call!']

#baseado na derivacao de <Exp.> se faz uma funcao
def exp(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] == '(': #caso parentesis aberto
            outputText[-1] += '('#adiciona parentesis aberto na saida
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':#precisa fechar o parentesis
                outputText[-1] += ')'#adiciona parentesis fechado na saida
                return barExp(txt[1:], l, c + 1)
            return [False, txt, l, c, 'Missing ")"!']
        elif isLetter(txt[0]):#caso comece com letra
            currentName = txt[0]#comeca a leitura de um identificador
            result = barId(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return expId(result[1], result[2], result[3])
        elif txt[0] == '0':#caso comece com zero
            outputText[-1] += '0'#numeros sao escritos da mesma forma na saida
            return barExp(txt[1:], l , c + 1)
        elif txt[0] >= '1' and txt[0] <= '9': #caso comece com numero > 0
            outputText[-1] += txt[0]#numeros sao escritos da mesma forma na saida
            result = barNum(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return barExp(result[1], result[2], result[3])
    return [False, txt, l, c, 'Invalid expression!']
            
            

#baseado na derivacao de <Num.(com barra)> se faz uma funcao
def barNum(txt, l, c):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    if len(txt) > 0 and txt[0] >= '0' and txt[0] <= '9': #caso ainda seja um numero
        outputText[-1] += txt[0]#numeros sao escritos da mesma forma na saida
        return barNum(txt[1:], l, c + 1)
    return [True, txt, l, c]#caso vazio

#baseado na derivacao de <Exp.(com barra)> se faz uma funcao
def barExp(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0 and txt[0] in '+-*/':#caso seja uma operacao
        outputText[-1] += txt[0]#operadores sao escritos da mesma forma na saida
        if txt[0] == '/':#caso seja divisao escreve de novo para deixar inteira
            outputText[-1] += txt[0]
        result = exp(txt[1:], l, c + 1)
        if not result[0]:
            return result
        return barExp(result[1], result[2], result[3])
    return [True, txt, l, c]#caso vazio

#baseado na derivacao de <Exp.Id> se faz uma funcao. 
def expId(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] in '+-*/':#caso seja uma operacao
            #Esta funcao e chamada se antes vinha um identificador, logo currentName deve ser uma variavel valida
            varScope = None
            if currentName in varTable: #se a variavel existe
                for varData in varTable[currentName]:
                    if varData[0] in getLastStack():#se o escopo da variavel pode ser visto no escopo atual
                        if varScope == None or len(varScope[0]) < len(varData[0]):#escolhe o escopo menos geral
                            varScope = varData
            if varScope == None: #variavel nao existe erro semantico
                semanticErrors.append([l, c, 'Not found variable: ' + currentName + '!'])
            else:
                outputText[-1] += 'v' + str(varScope[1]) + txt[0]#escreve a variavel e o operador na expressao
                if txt[0] == '/':
                    outputText[-1] += txt[0]#no caso da divisao interia precisa escrever de novo
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return barExp(result[1], result[2], result[3])
        elif txt[0] == '(':#caso seja parentesis aberto
            #Esta funcao e chamada se antes vinha um identificador, logo currentName deve ser uma funcao valida
            currentFun.append(currentName)#para nao perder o nome da funcao e colocada no topo da pilha
            currentParameters.append(0)#as funcoes desta linguagem se diferenciam pelo numero de parametros (em outras linguagens devem ter uma lista indicando os tipos)
            outputText.append('')#adiciona um texto no topo para escrever os parametros
            result = lExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':#precisa fechar o parentesis
                funCallVerifier('', l, c, True)#verifica a corretude semantica do chamado a funcao e escreve na saida                
                return barExp(txt[1:], l, c + 1)
            return [False, txt, l, c, 'Missing ")"!']
    #Se chegou aqui nao vem nada depois do identificador, logo deve ser uma variavel
    varScope = None
    if currentName in varTable: #se a variavel existe
        for varData in varTable[currentName]:
            if varData[0] in getLastStack():#se o escopo da variavel pode ser visto no escopo atual
                if varScope == None or len(varScope[0]) < len(varData[0]):#escolhe o escopo menos geral
                    varScope = varData
    if varScope == None: #variavel nao existe erro semantico
        semanticErrors.append([l, c, 'Not found variable: ' + currentName + '!'])
    else:
        outputText[-1] += 'v' + str(varScope[1])#escreve a variavel
    return [True, txt, l, c]#caso vazio

#funao adicionada para verificar o chamado a funcoes da linguagem
def languageFunCall(prefix, l, c, calling):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    if currentFun[-1] == 'result':#atribui valor ao resultado da funcao
        if currentParameters[-1] == 1 and calling:
            res = prefix + 'result = ' + outputText.pop()#escreve valor para resultado
            if trim(outputText[-1], l, c)[0] == '':
                outputText[-1] += res
            else:
                semanticErrors.append([l, c, 'Wrong use of result function, called in the middle of expression!'])
        else: #palavra reservada, precisa ter um parametro erro semantico
            semanticErrors.append([l, c, 'Wrong use of result function, called with ' + str(currentParameters[-1]) + ' parameters!'])
        return True 
    elif currentFun[-1] == 'print':#imprime valor
        params = ''
        n = currentParameters[-1]
        if outputText[-1] == '':
            n += 1
        for i in range(0, n):#le os parametros empilhados
            if len(params) > 0:
                params = ',' + params
            params = outputText.pop() + params
        res = prefix + 'myPrint(' + params + ')'
        if calling:
            outputText[-1] += res
        else:
            print(calling, trim(outputText[-1], l, c)[0])
            semanticErrors.append([l, c, 'print function cannot be defined!'])
        return True
    elif currentFun[-1] == 'scan':#le valor
        if currentParameters[-1] <= 1 and calling:   
            params = outputText.pop()
            outputText[-1] += prefix + 'int(input(' + params + '))'
        else: #palavra reservada, nao pode ter mais de um parametro erro semantico
            semanticErrors.append([l, c, 'Wrong use of scan function, called with ' + str(currentParameters[-1]) + ' parameters!'])
        return True
    return False

#funcao adicionada para verificar chamados a funcao que devem existir (chamada apos finalizacao do chamado)
def funCallVerifier(prefix, l, c, calling):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    if not languageFunCall(prefix, l, c, calling): # se nao for um chamado a funcao da linguagem entao analisa 
        #finalizado o chamado, se verifica se a funcao existe com essa quantidade de parametros
        funData = None
        if currentFun[-1] in funTable:
            for data in funTable[currentFun[-1]]:
                if data[0] == currentParameters[-1] and data[2] in getLastStack():
                    if funData == None or funData[1] < data[1]:
                        funData = data
        if funData == None:#funcao nao existe erro semantico
            semanticErrors.append([l, c, 'Not found function: ' + currentFun[-1] + ' with ' + str(currentParameters[-1]) + ' parameters!'])
        else:
            params = ''
            n = currentParameters[-1]
            if outputText[-1] == '':
                n += 1
            for i in range(0, n):#le os parametros empilhados
                if len(params) > 0:
                    params = ',' + params
                params = outputText.pop() + params
            if currentParameters[-1] == 0:
                outputText.pop()
            if calling:
                outputText[-1] += prefix + 'f' + funData[1].replace('-', 'f') + '(' + params + ')'#escreve o chamado a funcao
            else:
                outputText.append(prefix + 'f' + funData[1].replace('-', 'f') + '(' + params + ')')#adiciona o chamado para ser usado como definicao
    currentFun.pop()
    currentParameters.pop()


#baseado na derivacao de <L.Exp> se faz uma funcao. Esta e para lista de expressoes, so acontece quando e parametros de funcao
def lExp(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] == '(':#caso comece com parentesis aberto
            outputText[-1] += '('#so adiciona o parentesis aberto
            currentParameters[-1] = 1#tem pelo menos um parametro
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':#precisa fechar o parentesis
                outputText[-1] += ')'#so adiciona o parentesis fechado
                result = barExp(txt[1:], l, c + 1)
                if not result[0]:
                    return result
                return barLExp(result[1], result[2], result[3])
            return [False, txt, l, c, 'Missing ")"!']
        elif isLetter(txt[0]):#caso comece com letra
            currentParameters[-1] = 1#tem pelo menos um parametro
            currentName = txt[0]#comeca a leitura de um identificador, que logo sera tratado pelo expId (funcao anterior)
            result = barId(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = expId(result[1], result[2], result[3])
            if not result[0]:
                return result
            return barLExp(result[1], result[2], result[3])
        elif txt[0] == '0':#caso comece com zero
            outputText[-1] += '0'#so adiciona o numero lido
            currentParameters[-1] = 1#tem pelo menos um parametro
            result = barExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return barLExp(result[1], result[2], result[3])
        elif txt[0] >= '1' and txt[0] <= '9':#caso seja um numero >0
            outputText[-1] += txt[0]#so adiciona o numero lido
            currentParameters[-1] = 1#tem pelo menos um parametro
            result = barNum(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            return barLExp(result[1], result[2], result[3])
    return [False, txt, l, c]

    
#baseado na derivacao de <L.Exp (com barra)> se faz uma funcao. Chamada para separar os parametros de funcao por virgulas
def barLExp(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0 and txt[0] == ',':#caso comece com virgula
        #Novo parametro encontrado, logo cria uma nova entrada no topo
        outputText.append('')
        currentParameters[-1] += 1
        result = exp(txt[1:], l, c + 1)
        if not result[0]:
            return result
        return barLExp(result[1], result[2], result[3])
    return [True, txt, l, c]#caso vazio

#baseado na derivacao de <Fun.> se faz uma funcao
def fun(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] == ')':#caso feche parentesis
            return emptyFun(txt[1:], l , c + 1)
        elif txt[0] == '(':#caso abra parentesis, e um chamado a funcao
            outputText[-1] += '('#adiciona o parentesis aberto na saida
            currentParameters[-1] = 1#tem pelo menos um parametro
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':#precisa fechar o parentesis
                outputText[-1] += ')'#adiciona o parentesis fechado na saida
                result = barExp(txt, l, c + 1)
                if not result[0]:
                    return result
                result = barLExp(result[1], result[2], result[3])
                if not result[0]:
                    return result
                trimmed = trim(result[1], result[2], result[3])
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
                if len(txt) > 0 and txt[0] == ')':
                    #Verifica se a funcao chamada existe e imprime na saida
                    funCallVerifier('\t' * len(stack), l, c, True)
                    return [True, txt[1:], l, c + 1]
            return [False, txt, l, c, 'Missing ")"!']
        elif isLetter(txt[0]):#caso comece com letra
            currentParameters[-1] = 1#tem pelo menos um parametro
            currentName = txt[0]#comeca ler o identificador atual
            result = barId(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return funId(result[1], result[2], result[3])
        elif txt[0] == '0':#caso comece com zero, e um chamado a funcao
            currentParameters[-1] = 1#tem pelo menos um parametro
            outputText[-1] += '0'#adiciona o zero
            result = barExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #Verifica se a funcao chamada existe e imprime na saida
                funCallVerifier('\t' * len(stack), l, c, True)
                return [True, txt[1:], l, c + 1]
            return [False, txt, l, c, 'Missing ")"!']
        elif txt[0] >= '1' and txt[0] <= '9':#comeca com numero >0, e um chamado a funcao
            currentParameters[-1] = 1#tem pelo menos um parametro
            outputText[-1] = txt[0]#adiciona o digito
            result = barNum(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #Verifica se a funcao chamada existe e imprime na saida
                funCallVerifier('\t' * len(stack), l, c, True)
                return [True, txt[1:], l, c + 1]
            return [False, txt, l, c, 'Missing ")"!']
    return [False, txt, l, c]
            

#baseado na derivacao de <Empty Fun.> se faz uma funcao. Chamada ou definicao de funcao sem parametros
def emptyFun(txt_original, line, column):    
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0 and txt[0] == '=': #se define uma funcao
        trimmed = trim(txt[1:], l, c + 1)
        txt = trimmed[0]
        l = trimmed[1]
        c = trimmed[2]    
        if len(txt) > 0 and txt[0] == '{':#comeca abrindo chaves
            scope += 1 #comeca um novo escopo
            lastStack = getLastStack()
            stack.append(lastStack + '-' + str(scope))#adiciona o escopo na pilha
            funTable[currentFun[-1]].append(0, stack[-1], lastStack)#adiciona os dados da funcao relacionando-os com o nome
            outputText.append('')#adiciona um elemento no topo da pilha para escrever o escopo da função
            #copia pilha
            tempSatck = stack
            stack = [stack[-1]]
            result = program(txt[1:], l, c + 1)
            #recupera pilha
            stack = tempStack
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == '}':#precisa fechar a chave
                outputFun = 'def f' + stack[-1].replace('-', 'f') + '():\n\tresult = 0\n' + outputText.pop()#obtem a traducao da funcao
                if len(outputText) == 0:
                    outputText.append('')
                outputText[0] = outputFun + '\n\treturn result\n\n' + outputText[0]#coloca a funcao na saida principal
                stack.pop()#fecha o escopo da funcao
                currentFun.pop()#apos analisar a funcao sem parametros eliminar o nome dela da pilha
                currentParameters.pop()#eleminhar a entrada criada para ela na pilha de parametros
                return [True, txt[1:], l, c + 1]
            return [False, txt, l, c, 'Missing "}"!']
        return [False, txt, l, c, 'Missing "{"!']
    else:
        #se realiza chamada da funcao sem parametros
        funCallVerifier('\t' * len(stack), l, c, True)
    return [True, txt, l, c]#caso vazio


def funReplaceParametersByVariables(l, c):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    #substitui os valores para cada uma das variaveis que foram contabilizadas nos parametros
    for i in range(1, currentParameters[-1] + 1):
        varScope = None
        if len(outputText[-i]) > 0:
            if outputText[-i] in varTable: #se a variavel existe
                for varData in varTable[outputText[-i]]:
                    if varData[0] in getLastStack():#se o escopo da variavel pode ser visto no escopo atual
                        if varScope == None or len(varScope[0]) < len(varData[0]):#escolhe o escopo menos geral
                            varScope = varData
            if varScope == None: #variavel nao existe erro semantico
                semanticErrors.append([l, c, 'Not found variable: ' + outputText[-i] + '!'])
            else:
                outputText[-i] = 'v' + str(varScope[1])#escreve a variavel traduzida


def funCreateParametersScope(l, c):
    global varsNumber, varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    #cria variaveis de escopo para os parametros (definicao de funcao)
    for i in range(1, currentParameters[-1] + 1):
        if len(outputText[-i]) > 0:
            if outputText[-i] not in varTable: #se a variavel nao existe
                varTable.update({outputText[-i]:[]})
            elif getLastStack() in varTable[outputText[-i]]:
                semanticErrors.append([l, c, 'Repeated identifier in function definition: ' + outputText[-i] + '!'])
            #adiciona o escopo
            varTable[outputText[-i]].append([getLastStack(), varsNumber])
            outputText[-i] = 'v' + str(varsNumber)#escreve a variavel traduzida
            varsNumber += 1

#baseado na derivacao de <Fun.Id> se faz uma funcao
def funId(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] in '+-*/':#caso seja um operador e um chamado a funcao
            outputText[-1] = currentName#coloca a variavel que estava sendo lida
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            outputText[-1] += txt[0]#escreve o operador
            if txt[0] == '/':
                outputText[-1] += txt[0]#no caso da divisao inteira precisa escrever mais uma vez
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #se realiza chamada da funcao
                funCallVerifier('\t' * len(stack), l, c, True)
                return [True, txt[1:], l, c + 1]
        elif txt[0] == '(':#caso seja parentesis aberto e um chamado a funcao
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            currentFun.append(currentName)#adiciona chamado da funcao atual
            currentParameters.append(0)#adiciona contador de parametros para funcao atual
            outputText.append('')#apenda espaco para escrever parametros
            result = lExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':#fecha o parentesis
                #chama a funcao
                funCallVerifier('', l, c, True)
                result = barExp(txt[1:], l, c + 1)
                if not result[0]:
                    return result
                result = barLExp(result[1], result[2], result[3])
                if not result[0]:
                    return result
                trimmed = trim(result[1], result[2], result[3])
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
                if len(txt) > 0 and txt[0] == ')':
                    #se realiza chamada da funcao
                    funCallVerifier('\t' * len(stack), l, c, True)
                    return [True, txt[1:], l, c + 1]
        elif txt[0] == ',':#comeca com virgula, pode ser um chamado a funcao ou uma definicao
            currentParameters[-1] += 1#incrementa a quantidade de parametros
            outputText[-1] = currentName#coloca a variavel que estava sendo lida
            outputText.append('')#insere espaco para proximo parametro
            return list_(txt[1:], l, c + 1)
        elif txt[0] == ')': #fecha parentesis pode ser um chamado a funcao ou uma definicao
            outputText[-1] = currentName#escreve o identificador lido na saida, depois deve ser analisado se esse parametro e de definicao ou de chamado a funcao
            return afterParFunId(txt[1:], l, c + 1)
    return [False, txt, l, c]

#baseado na derivacao de <AfterParFunId> se faz a funcao
def afterParFunId(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0 and txt[0] == '=': #caso defina funcao
        trimmed = trim(txt[1:], l, c + 1)
        txt = trimmed[0]
        l = trimmed[1]
        c = trimmed[2]
        if len(txt) > 0 and txt[0] == '{':#precisa abrir chave para escrever a funcao
            scope += 1
            lastStack = getLastStack()
            stack.append(lastStack + '-' + str(scope))
            #adiciona as informacoes da funcao na tabela
            funTable[currentFun[-1]].append([currentParameters[-1], stack[-1], lastStack])
            #cria variaveis no escopo da funcao para cada um dos parametros
            funCreateParametersScope(l, c)
            #adiciona saida para corpo da funcao
            outputText.append('')
            #variavel temporal para stack
            tempStack = stack
            stack = [stack[-1]]
            result = program(txt[1:], l, c + 1)
            stack = tempStack            
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == '}':#fecha a chave
                #pega corpo da funcao
                funBody = outputText.pop()
                #adiciona linha para escrever cabecalho 
                outputText.append('')
                #escreve como chamada de funcao
                funCallVerifier('', l, c, False)
                stack.pop()
                #escreve na saida a funcao
                res = 'def ' + outputText.pop() + ':\n\tresult = 0\n' + funBody + '\n\treturn result\n\n'
                if len(outputText) == 0:
                    outputText.append('')
                outputText[0] = res + outputText[0]
                return [True, txt[1:], l, c + 1]
            return [False, txt, l, c, 'Missing "}"!']
        return [False, txt, l, c, 'Missing "{"!']
    else:
        #chamado a funcao
        funReplaceParametersByVariables(l, c)
        funCallVerifier('\t' * len(stack), l, c, True)
    return [True, txt, l, c]#caso vazio

#baseado na derivacao de <List> se faz uma funcao
def list_(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] == '(':#chamado a funcao
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            outputText[-1] += '('#escreve o parentesis aberto
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                outputText[-1] += ')'#escreve o parentesis fechado
                result = barExp(txt[1:], l, c + 1)
                if not result[0]:
                    return result
                result = barLExp(result[1], result[2], result[3])
                if not result[0]:
                    return result
                trimmed = trim(result[1], result[2], result[3])
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
                if len(txt) > 0 and txt[0] == ')':
                    #se realiza chamada da funcao
                    funCallVerifier('\t' * len(stack), l, c, True)
                    return [True, txt[1:], l, c + 1]
        elif txt[0] == '0': #chamado a funcao
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            outputText[-1] += '0'#escreve o zero
            result = barExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #se realiza chamada da funcao
                funCallVerifier('\t' * len(stack), l , c, True)
                return [True, txt[1:], l, c + 1]
        elif txt[0] >= '1' and txt[0] <= '9':#chamado a funcao
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            outputText[-1] += txt[0]#escreve o digito
            result = barNum(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #se realiza chamada da funcao
                funCallVerifier('\t' * len(stack), l, c, True)
                return [True, txt[1:], l, c + 1]
        elif isLetter(txt[0]):#pode ser definicao ou chamado de funcao
            currentName = txt[0]#comeca ler o identificador atual
            result = barId(txt[1:], l, c + 1)
            if not result[0]:
                return result
            return listId(result[1], result[2], result[3])
    return [False, txt, l, c]
            

#baseado na derivacao de <List Id> se faz uma funcao
def listId(txt_original, line, column):
    global varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors, outputText
    trimmed = trim(txt_original, line, column)
    txt = trimmed[0]
    l = trimmed[1]
    c = trimmed[2]
    if len(txt) > 0:
        if txt[0] in '+-/*':#caso seja um operador e um chamado a funcao
            outputText[-1] = currentName#coloca o identificador que esta sendo lido
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            outputText[-1] += txt[0]#escreve o operador
            if txt[0] == '/':
                outputText[-1] += txt[0]#caso seja divisao, escreve de novo para deixar inteira
            result = exp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            result = barExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            result = barLExp(result[1], result[2], result[3])
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #se realiza chamada da funcao
                funCallVerifier('\t' * len(stack), l, c, True)
                return [True, txt[1:], l, c + 1]
        elif txt[0] == '(':#chamado a funcao
            funReplaceParametersByVariables(l, c)#troca os identificadores na funcao por variaveis que devem existir
            currentFun.append(currentName)#adiciona chamado da funcao atual
            currentParameters.append(0)#adiciona contador de parametros para funcao atual
            outputText.append('')#apenda espaco para escrever parametros
            #outputText[-1] += '('#escreve o parentesis aberto
            result = lExp(txt[1:], l, c + 1)
            if not result[0]:
                return result
            trimmed = trim(result[1], result[2], result[3])
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == ')':
                #chama a funcao
                funCallVerifier('', l, c, True)
                result = barExp(txt[1:], l, c + 1)
                if not result[0]:
                    return result
                result = barLExp(result[1], result[2], result[3])
                if not result[0]:
                    return result
                trimmed = trim(result[1], result[2], result[3])
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
                if len(txt) > 0 and txt[0] == ')':
                    #se realiza chamada da funcao
                    funCallVerifier('\t' * len(stack), l, c, True)
                    return [True, txt[1:], l, c + 1]
        elif txt[0] == ',':#comeca com virgula, pode ser um chamado a funcao ou uma definicao
            currentParameters[-1] += 1#incrementa a quantidade de parametros
            outputText[-1] = currentName#coloca o dientificador que se leu
            outputText.append('')#insere espaco para proximo parametro
            return list_(txt[1:], l, c + 1)
        elif txt[0] == ')':
            outputText[-1] = currentName#coloca o ultmo identificador lido
            trimmed = trim(txt[1:], l, c + 1)
            txt = trimmed[0]
            l = trimmed[1]
            c = trimmed[2]
            if len(txt) > 0 and txt[0] == '=':
                trimmed = trim(txt[1:], l, c + 1)
                txt = trimmed[0]
                l = trimmed[1]
                c = trimmed[2]
                if len(txt) > 0 and txt[0] == '{':
                    scope += 1
                    lastStack = getLastStack()
                    stack.append(lastStack + '-' + str(scope))
                    #adiciona as informacoes da funcao na tabela
                    funTable[currentFun[-1]].append([currentParameters[-1], stack[-1], lastStack])
                    #cria variaveis no escopo da funcao para cada um dos parametros
                    funCreateParametersScope(l, c)
                    #adiciona saida para corpo da funcao
                    outputText.append('')
                    #variavel temporal para stack
                    tempStack = stack
                    stack = [stack[-1]]
                    result = program(txt[1:], l, c + 1)
                    stack = tempStack
                    if not result[0]:
                        return result
                    trimmed = trim(result[1], result[2], result[3])
                    txt = trimmed[0]
                    l = trimmed[1]
                    c = trimmed[2]
                    if len(txt) > 0  and txt[0] == '}':
                        #pega corpo da funcao
                        funBody = outputText.pop()
                        #adiciona linha para escrever cabecalho 
                        outputText.append('')
                        #escreve como chamada de funcao
                        funCallVerifier('', l, c, False)
                        stack.pop()
                        #escreve na saida a funcao
                        res = 'def ' + outputText.pop() + ':\n\tresult = 0\n' + funBody + '\n\treturn result\n\n'
                        if len(outputText) == 0:
                            outputText.append('')
                        outputText[0] = res + outputText[0]
                        return [True, txt[1:], l, c + 1]            
    return [False, txt, l, c, 'Syntax error!']


#metodo principal, para reconhecer deve consumir a string completa
def recognizes(txt):
    global varsNumber, varTable, stack, scope, currentName, currentFun, currentParameters, currentVar, outputText, semanticErrors
    result = program(txt, 1, 0)
    if (result[0] and len(result[1]) == 0):
        if len(semanticErrors) == 0:
            outputText[0] = 'def myPrint(*params):\n\tprint(params)\n\treturn 0\n\n' + outputText[0]
            print(outputText[0])
        else:
            varsNumber = 0
            varTable = {}
            stack = []            
            scope = 0            
            currentName = ''            
            currentFun = []            
            currentParameters = []            
            currentVar = ''
            outputText = ['']
            semanticErrors = []
            result = program(txt, 1, 0)
            if len(semanticErrors) == 0:
                outputText[0] = 'def myPrint(*params):\n\tprint(params)\n\treturn 0\n\n' + outputText[0]
                print(outputText[0])
            else:
                for error in semanticErrors:
                    print('Semantic error at line', error[0], 'and column', str(error[1]) + '.', error[2])
    else:
        if len(result) == 5:
            print('Error at line', result[2], 'and column', str(result[3]) + '.', result[4])
        else:
            print('Error at line', result[2], 'and column', str(result[3]) + '. Syntax error!')
        print('Not processed code:', result[1])
