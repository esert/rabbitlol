get_id = function(id) {
  return document.getElementById(id);
};

submit = function(id, alert_text) {
  if (alert_text !== undefined && !confirm(alert_text)) {
    return;
  }
  get_id(id).submit();
};

hide = function(id) {
  get_id(id).hidden = true;
};

show = function(id) {
  get_id(id).hidden = false;
};

get_checkboxes = function() {
  var out = [];
  var inputs = document.getElementsByTagName('input');
  for (var i in inputs) {
    var input = inputs[i];
    if (input.type === 'checkbox') {
      out.push(input);
    }
  }
  return out;
};

select_all = function() {
  get_checkboxes().forEach(
    function(x) {
      x.checked = true;
    }
  );
};

select_none = function() {
  get_checkboxes().forEach(
    function(x) {
      x.checked = false;
    }
  );
};
