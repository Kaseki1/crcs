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
      <div class="row">
        <div class="col-7">
          <div class="card">
            <div class="card-header">
              Безопасность профиля
            </div>
            <div class="card-body">
                <div>
                  Статус почты: <a href="#" class="btn btn-dark" style="color: whitesmoke;">Подтвердить почту</a>
                </div>
                <div style="margin-top: 10px;">
                  Статус пароля: <a href="#" class="btn btn-dark" style="color: whitesmoke;">Сменить пароль</a>
                </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              Активные сессии
            </div>
            <div class="card-body">
                
            </div>
          </div>
        </div>
        <div class="col-5">
          <div class="card">
            <div class="card-header">
              Клиентские пулы
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                <li class="list-group-item">
                  <a href="#" class="btn btn-dark" style="color: whitesmoke; width: 100%;">Создать пул</a>
                </li>
                <li class="list-group-item">
                  <!-- TODO: ЗДЕСЬ БУДЕТ СПИСОК ПУЛОВ -->
                  <a href="#">► POOL: 000000</a><br />
                  <a href="#">► POOL: 000000</a><br />
                  <a href="#">► POOL: 000000</a><br />
                  <a href="#">► POOL: 000000</a><br />
                  <a href="#">► POOL: 000000</a><br />
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>