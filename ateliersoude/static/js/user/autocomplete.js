let inputEmailSelector = 'input[name="email"]';
let inputs = document.querySelectorAll(inputEmailSelector);

inputs.forEach(function (node) {
    new autoComplete({
        selector: node,
        minChars: 3,
        source: function(user, suggest){
            term = user.toLowerCase();
            var choices = JSON.parse(document.getElementById('users-data').textContent);
            var matches = [];
            for (i=0; i<choices.length; i++)
              if (~choices[i].toLowerCase().indexOf(term)) matches.push(choices[i]);
            suggest(matches);
        }
    });
});
