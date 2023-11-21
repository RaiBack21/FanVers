<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

<script type="text/javascript">
  $(document).ready(function () {
    $("input.end_date").change(function() {
      const start = document.querySelector("#start_date");
      var start_date = start.value
      const end = document.querySelector("#end_date");
      var end_date = end.value
      const loc = document.querySelector("#location");
      var location = loc.value
        $.get("ajax_cost/?start_date="+start_date+"&end_date="+end_date+"&location="+location, function(data) {
          $("#target, #cost1").html(data);
          $("#cost1").attr("value", data);
        });
      });
    });
</script>
<script>
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxPrefilter(function(options, originalOptions, jqXHR){
    if (options['type'].toLowerCase() === "post") {
        jqXHR.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    }
});
</script>

<script type="text/javascript">
  $(document).ready(function () {
    $("input.end_datec").change(function() {
      const start = document.querySelector("#start_datec");
      var start_date = start.value
      const end = document.querySelector("#end_datec");
      var end_date = end.value
      const loc = document.querySelector("#locationc");
      var location = loc.value
        $.get("ajax_cost/?start_date="+start_date+"&end_date="+end_date+"&location="+location, function(data) {
          $("#targetc").html(data);
          $("#cost2").attr("value", data);
        });
      });
    });
</script>

<script type="text/javascript">
  $(document).ready(function () {
    $("select.gg").click(function() {
      const start = document.querySelector("#start_dateg");
      var start_date = start.value
      const end = document.querySelector("#end_dateg");
      var end_date = end.value
      const loc = document.querySelector("#locationg");
      var location = loc.value
      const genr = document.querySelector("#genres")
      var genre = genr.value
        $.get("ajax_cost/?start_date="+start_date+"&end_date="+end_date+"&location="+location+"&genre="+genre, function(data) {
          $("#targetg").html(data);
          $("#cost3").attr("value", data);
        });
      });
    });
</script>

<script type="text/javascript">
  $(document).ready(function () {
    $("select.tt").click(function() {
      const start = document.querySelector("#start_datet");
      var start_date = start.value
      const end = document.querySelector("#end_datet");
      var end_date = end.value
      const loc = document.querySelector("#locationt");
      var location = loc.value
      const ta = document.querySelector("#tags")
      var tag = ta.value
        $.get("ajax_cost/?start_date="+start_date+"&end_date="+end_date+"&location="+location+"&tag="+tag, function(data) {
          $("#targett").html(data);
          $("#cost4").attr("value", data);
        });
      });
    });
</script>


<script type="text/javascript">
  $(document).ready(function () {
    $("select.ff").click(function() {
      const start = document.querySelector("#start_datef");
      var start_date = start.value
      const end = document.querySelector("#end_datef");
      var end_date = end.value
      const loc = document.querySelector("#locationf");
      var location = loc.value
      const fando = document.querySelector("#fandom")
      var fandom = fando.value
        $.get("ajax_cost/?start_date="+start_date+"&end_date="+end_date+"&location="+location+"&fandom="+fandom, function(data) {
          $("#targetf").html(data);
          $("#cost5").attr("value", data);
        });
      });
    });
</script>

<script type="text/javascript">
  $(document).ready(function () {
    $("#test, #catalog, #genre, #tag, #fandoms").click(function() {
      var cost1 = $("#cost1").attr("value");
      var cost2 = $("#cost2").attr("value");
      var cost3 = $("#cost3").attr("value");
      var cost4 = $("#cost4").attr("value");
      var cost5 = $("#cost5").attr("value");
      $.get("ajax_cost_sum/?cost1="+cost1+"&cost2="+cost2+"&cost3="+cost3+"&cost4="+cost4+"&cost5="+cost5, function(data) {
        $("#targetsum").html(data);
        $("#targetsum").attr("value", data);
      })
    })
  })
</script>


<script>
  $(document).ready(function () {
    $("#save").click(function() {
      const start = document.querySelector("#start_date");
      var start_date = start.value
      const end = document.querySelector("#end_date");
      var end_date = end.value
      const loc = document.querySelector("#location");
      var location = loc.value

      const startc = document.querySelector("#start_datec");
      var start_datec = startc.value
      const endc = document.querySelector("#end_datec");
      var end_datec = endc.value
      const locc = document.querySelector("#locationc");
      var locationc = locc.value

      const startg = document.querySelector("#start_dateg");
      var start_dateg = startg.value
      const endg = document.querySelector("#end_dateg");
      var end_dateg = endg.value
      const locg = document.querySelector("#locationg");
      var locationg = locg.value
      const genr = document.querySelector("#genres")
      var genre = genr.value

      const startt = document.querySelector("#start_datet");
      var start_datet = startt.value
      const endt = document.querySelector("#end_datet");
      var end_datet = endt.value
      const loct = document.querySelector("#locationt");
      var locationt = loct.value
      const ta = document.querySelector("#tags")
      var tag = ta.value

      const startf = document.querySelector("#start_datef");
      var start_datef = startf.value
      const endf = document.querySelector("#end_datef");
      var end_datef = endf.value
      const locf = document.querySelector("#locationf");
      var locationf = locf.value
      const fando = document.querySelector("#fandom")
      var fandom = fando.value

      var cost1 = $("#cost1").attr("value");
      var cost2 = $("#cost2").attr("value");
      var cost3 = $("#cost3").attr("value");
      var cost4 = $("#cost4").attr("value");
      var cost5 = $("#cost5").attr("value");

      var cost = $("#targetsum").attr("value");

      var csrf = $("input[name=csrfmiddlewaretoken]").val()

      document.location.href = 'http://localhost:8000/Advertisement/book/1/advertisement/';
      $.post("", {'cost': cost, 'start_date': start_date, 'end_date': end_date,
       'location': location, 'start_datec': start_datec, 'end_datec': end_datec,
        'locationc': locationc, 'start_dateg': start_dateg, 'end_dateg': end_dateg,
         'locationg': locationg, 'genre': genre, 'start_datet': start_datet,
         'end_datet': end_datet, 'locationt': locationt, 'tag': tag,
         'start_datef': start_datef, 'end_datef': end_datef,
         'locationf': locationf, 'fandom': fandom, 'cost1': cost1,
         'cost2': cost2, 'cost3': cost3, 'cost4': cost4, 'cost5': cost5}, function(data) {
           $("#message").html(data);
           document.location.href = document.location
      })
    })
  })
</script>
