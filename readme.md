Telegram mailing tool
Программа предназначена для рассылки сообщений абонентам в telegram от лица зарегистрированного в telegram оператора программы (user bot) средствами telegram api. 
Работа осуществляется из командной строки. В файл “contacts.ml” записывается контакты оператора в telegram.
Далее сам оператор должен из этого списка выбрать контакты для рассылки и поместить их в файл “list.ml”. 
При запуске программы из этого файла считывается список рассылки, анализируется на ошибки и повторы. 
Из файла “message.ml” считывается сообщение и отсылается оператору в telegram для проверки. 
Оператор может откорректировать сообщение и отправить его себе повторно, либо, если сообщение его устраивает, осуществить рассылку. 
По ходу рассылки, если не удается отправить сообщение, выводится сообщение об ошибке с указанием контакта. 
После окончания рассылки формируется файл с результатами – “results.ml”. 
Что бы повторить рассылку, необходимо запустить программу заново.