from seguranca import Seguranca

s = Seguranca()
print("Pasta workspace:", s.validar_caminho("teste.txt"))
print("Confirmação de segurança:")
print(s.confirmar_acao("teste de autorização"))
