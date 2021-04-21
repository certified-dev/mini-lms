$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-tma .modal-content").html("");
        $("#modal-tma").modal("show");
      },
      success: function (data) {
        $("#modal-tma .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#tma-table tbody").html(data.html_tma_list);
          $("#modal-tma").modal("hide");
        }
        else {

          Swal.fire({
            title: 'Warning!',
            text: 'Record Already Exists!',
            icon: 'warning',
            confirmButtonText: 'Ok'
            })

          $("#modal-tma .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };
  
  $(".taken_tma_view").click(function(){
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      success: function (data) {
          $("#modal-tma .modal-content").html(data.html_form);
        $("#modal-tma").modal("show");

      }
    });
    });

  /* Binding */

  // Create tma
  $(".js-create-tma").click(loadForm);
  $("#modal-tma").on("submit", ".js-tma-create-form", saveForm);

  // Update tma
  $("#tma-table").on("click", ".js-update-tma", loadForm);
  $("#modal-tma").on("submit", ".js-tma-update-form", saveForm);

  // Delete tma
  $("#tma-table").on("click", ".js-delete-tma", loadForm);
  $("#modal-tma").on("submit", ".js-tma-delete-form", saveForm);

});