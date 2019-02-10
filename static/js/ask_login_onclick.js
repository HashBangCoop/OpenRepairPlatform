
function ask_login_onclick(){
    var message = "Vous devez vous connecter ou créer un compte pour vous inscrire";
    var callback
    callback = () => window.location.replace("/auth/login");
    create_modal_window(message, callback);
}
