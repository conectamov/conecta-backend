class BotResponses:
    
    def could_not_find_match():
        message = ("😕 Não encontramos conexões nessa página.\n\n"
        "Tente outra página ou envie *match* novamente "
        "para explorar mais pessoas ✨")
        return message

    def received_request_match(user):
        message = ("✨ Você recebeu um pedido de conexão no Conecta!\n\n"
        f"👤 *{user.name}*\n"
        f"🤝 Compatibilidade de interesses: *{percent}%*\n\n"
        "👉 Para aceitar, envie:\n"
        f"*conectar {user.id}*")
        return message

    def created_connection_success(user):
        message = (f"🎉 Conexão criada com *{user.name}*!\n\n"
        "Agora vocês já podem conversar e trocar ideias 💬\n"
        "Comece enviando uma mensagem agora mesmo 🚀")
        return message
    

    #help messages
    def welcome_message(user):
        message = (
            f"Olá, {user.name}!\n"
            "🤔 Não entendi muito bem essa mensagem.\n\n"
            "Aqui vão algumas coisas que você pode fazer:\n"
            "• Enviar *match* para ver pessoas com interesses parecidos\n"
            "• Enviar *match 2*, *match 3*, etc. para navegar pelas páginas\n"
            "• Enviar *conectar ID* para se conectar com alguém\n\n"
            "Se quiser começar do zero, é só mandar *match* ✨"
        )
        return message
    

    #questions
    def ask_name():
        message = ("Qual é o seu nome?")
        return message
    
    def ask_subjects():
        message = ("Quais matérias você mais gosta ou tem mais interesse?")     
        return message
    
    def ask_level():
        message = (
            "Conte-nos mais sobre sua história. Como você descreveria seu nível atual como estudante?\n"
            "Ex: ensino médio, 2º ano, ensino técnico, estudando por conta própria"
        )

        return message



    def ask_interest():
        message = (
            "Quais são seus interesses no momento?\n"
            "Ex: escrever debates, olimipíadas, tecnologia, projetos sociais, intercâmbio, inteligência artificial..."
        )

        return message
    

    def ask_opportunities():
        message = ("Você gostaria de receber oportunidades que combinem com você? (*Sim* ou *Não*)")
        return message
    def yes_or_no_answer():
        message = ("Por favor, responda apenas com *Sim* ou *Não*.")
        return message
    def ask_opportunities_2():
        message = ("Você gostaria de receber oportunidades que combinem com você?")
        return message   
    
    def ask_matching():
        message = ("Você gostaria de se conectar com outros estudantes? (*Sim* ou *Não*)")
        return message
    
    def ask_matching_2():
        message = ("Você gostaria de se conectar com outros estudantes?")
        return message
     
    
    def analysing_answers():
        message = ("Perfeito! Estou analisando suas respostas 🤔")
        return message
    
    def inappropriated_answer():
        message = (                
            "Não conseguimos para entender muito bem sua resposta 🤔\n"
            "Ela ficou pouco detalhada ou não se encaixa no que estamos perguntando.\n\n"
            "Pode explicar melhor? Quanto mais detalhes, melhor para te ajudar 😊"
        )
        return message
    
    def created_profile_success(user_name):
        message = f"Tudo certo, {user_name}! Seu perfil foi criado com sucesso 🚀"
        return message
    

    #controller handling
    def user_matching_unavailable():
        message = (
            "🚫 Essa pessoa não está disponível para conexões no momento.\n\n"
            "Mas não se preocupe! Existem outras pessoas incríveis "
            "que podem combinar com você.\n\n"
            "Envie *match* para continuar explorando ✨"
        )
        return message
    
    def match_request_has_been_sent():
        message = (
            "📨 Pedido de conexão enviado com sucesso!\n\n"
            "Agora é só aguardar 😊\n"
            "Assim que a pessoa aceitar, eu te aviso aqui mesmo.\n\n"
            "Enquanto isso, você pode enviar *match* para conhecer mais pessoas ✨"
        )
        return message