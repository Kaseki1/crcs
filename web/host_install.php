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

    <title>CRCS | Установка</title>
  </head>
  <body>
    <?=require_once "includes/header.php"?>
    <main class="container" style="margin-top: 80px">
      <div class="card">
        <div class="card-header">
          <h2>Установка клиентской части.</h2>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            <li class="list-group-item">
              <h2>Установка для Linux (Debian-дистрибутивы)</h2>
              Для того, чтобы установить клиентский компонент на дистрибутив Ubuntu любой версии, вам нужно добавить наш пользовательский репозиторий через PPA:
              <div class="terminal-command">sudo add-apt-repository <b>НАЗВАНИЕ PPA</b></div>
              После чего обновите базу пакетов.
              <div class="terminal-command">sudo apt-get update</div>
              Теперь вы можете установить пакет в свою систему.
              <div class="terminal-command">sudo apt-get install <b>НАЗВАНИЕ ПАКЕТА</b></div>
            </li>
            <li class="list-group-item">
              <h2>Установка для Windows</h2>
              Для установки на Windows системы воспользуйтесь одним из представленных зеркал.
              <br/>
              <a class="download" href="#">Зеркало №1</a><br/>
              <a class="download" href="#">Зеркало №1</a><br/>
              <a class="download" href="#">Зеркало №1</a><br/>
              <a class="download" href="#">Зеркало №1</a>
            </li>
          </ul>
        </div>
      </div>
    </main>

    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>