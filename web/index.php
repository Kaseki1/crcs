<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="img/favicon.ico" type="image/x-icon">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <!-- Hack Font -->
    <link rel="stylesheet" type="text/css" href="fonts/hack/style.css">

    <!-- Custom styles -->
    <link rel="stylesheet" type="text/css" href="css/style.css">

    <title>CRCS | Главная</title>
  </head>
  <body>
    <?=require_once "includes/header.php"?>
    <main class="container">
      <div class="card">
        <div class="card-header">
          <h2>О нашем проекте</h2>
        </div>
        <div class="card-body" style="font-size: 12pt;">
          CRCS <em>(Centralized Remote Control System)</em> является нашей реализацией удаленного доступа. Наша система мультиплатформенная, безопасная во всех ее компонентах, а главное - абсолютно бесплатная. Стоит уточнить, что проект не является <b>"удаленкой"</b> в обычном понимании этого слова. Все исполняемые процессы на удаленной машине скрыты от глаз ее пользователя, проще говоря, вы используете API системы, а не получаете над ней контроль, словно ее непосредственный пользователь. Узнать поподробнее о том, как это работает, можно во вкладке "Документация".
        </div>
      </div>
      <center><h2 style="margin-top: 45px;">Установка</h2></center>
      <div class="row">
        <div class="col">
          <div class="card">
            <img style="width: 200px; margin: 20px; margin-left: auto; margin-right: auto;" class="card-img-top" src="https://img.icons8.com/ios-filled/344/cloud-access.png" alt="Card image cap">
            <div class="card-header">
              <h2>Участник сети.</h2>
            </div>
            <div class="card-body">
              Участник <em>(альтернативное название: "хосты")</em> - устанавливается на компьютер, доступ к которому в дальнейшем может получить администратор. Для получения инструкции по эксплуатации - нажмите на кнопку ниже.
              <br /><a style="margin-top: 44px;" class="btn btn-dark" href="host_install.php" role="button">Страница загрузки</a>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="card">
            <img style="width: 200px; margin: 20px; margin-left: auto; margin-right: auto;" class="card-img-top" src="https://img.icons8.com/ios-filled/344/command-line.png" alt="Card image cap">
            <div class="card-header">
              <h2>Админ панель.</h2>
            </div>
            <div class="card-body">
              Средство управления участниками сети или же хостами. Благодаря этой панели вы сможете исполнять команды на удаленных устройствах и получать результаты, создавать пулы, приглашать в пулы других администраторов и многое другое, что вы можете узнать в нашей документации.
              <br /><a style="margin-top: 20px;" class="btn btn-dark" href="admin_install.php" role="button">Страница загрузки</a>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h2>Новости обновлений</h2>
        </div>
        <div class="card-body">
          Здесь в дальнейшем будет изображен перечень обновлений и их описание.
        </div>
      </div>
    </main>
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>
