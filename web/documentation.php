<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <!-- Hack Font -->
    <link rel="stylesheet" type="text/css" href="fonts/hack/style.css">

    <!-- Custom styles -->
    <link rel="stylesheet" type="text/css" href="css/style.css">

    <title>CRCS | Документация</title>
  </head>
  <body>
    <?=require_once "includes/header.php"?>
    <main class="container" style="margin-top: 80px">
      <div class="card">
        <div class="card-header">
          <h2>Описание системы CRCS.</h2>
        </div>
        <div class="card-body">
          Данная система по удаленному управлению устройствами является централизованной, т.е. существует выделенный сервер, перенаправляющий ваши команды клиентам и возвращающий результаты их выполнения. Следовательно, появляется две
          роли: <b>администратор</b> и <b>хост</b>.
          
          <p><b>Шифрование</b>. Все пароли от учетных записей администраторов хешируются bcrypt - улучшенной хеш-функцией, основополагающей особенностью которой является искусственное замедление шифрования для значительного замедления процесса брут-форса. Все данные, пересылаемые на любом этапе <em>(от админа к серверу, от сервера к хосту и обратно)</em> шифруются SSL.</p>
          <p><b>Пул клиентов (Clients pool)</b> - это подобие виртуальной локальной сети <em>(VLAN)</em>, в которую входят клиенты. Из этого следует, что более корректнее говорить не "админ управляет клиентом", а "админ управляет пулом", т.к. именно администратор эти пулы создает. В пулы могут быть приглашены другие администраторы и одновременно управлять машинами из одной сети.</p>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h2>Документация по настройки клиентской части.</h2>
        </div>
        <div class="card-body">
            
        </div>
      </div>
    </main>

    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>