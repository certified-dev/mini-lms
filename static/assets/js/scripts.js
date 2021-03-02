$(document).ready(function () {

  const message_tag = $("#message_tag").text();
  const message = $("#message").text();

  const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: 'btn btn-success',
      cancelButton: 'btn btn-danger'
    },
    buttonsStyling: false
  })

  if ($("#message").length){
    
    if (message_tag === "alert-success") {

      Swal.fire({
        title: 'Success!',
        text: message,
        icon: 'success',
        confirmButtonText: 'Ok'
  
      })
  
    } else if (message_tag === "alert-danger") {
  
      Swal.fire({
        title: 'Error!',
        text: message,
        icon: 'error',
        confirmButtonText: 'Ok'
      })
  
    } else if (message_tag === "alert-warning") {
  
      Swal.fire({
        title: 'Warning!',
        text: message,
        icon: 'warning',
        confirmButtonText: 'Ok'
      })
  
    } else {
  
      Swal.fire({
        title: 'Info!',
        text: message,
        icon: 'info',
        confirmButtonText: 'Ok'
      })
  
    }

  }


  if ($("#semester").length){

  const semester =  JSON.parse($("#semester").text());
  const reg_open =  JSON.parse($("#reg_open").text());
  const sem_reg_status = JSON.parse($("#sem_reg_status").text());

  if (reg_open) {
  
    if (sem_reg_status) {
  
      Swal.fire({
        title: 'Semester Registration!',
        text: 'You Have Registered For This Semester',
        icon: 'success',
        confirmButtonText: 'Ok',
        footer: '<a href="/student/courses/">View Courses</a>'
    
      })
  
    } else {
  
      $("#Sem_Registration").modal('show');
  
    }
  
     } else {
  
    Swal.fire({
      title: 'Registration Closed',
      text: 'Course Registration Closed For The Semester.',
      icon: 'error',
      confirmButtonText: 'Ok'
    })
  
    }
  }

  if ($("#tma_page").length){

  const tma_page =  JSON.parse($("#tma_page").text());
  const course_count =  JSON.parse($("#course_count").text());
  const tma_count =  JSON.parse($("#tma_count").text());
  const tma_completed =  JSON.parse($("#tma_completed").text());

  if (course_count > 0){
  
    if (tma_count < 1){
    
      if (tma_completed){
     
        Swal.fire({
          title: 'Tutor Marked Assesment',
          text: 'T.M.A Completed!!!',
          icon: 'success',
          confirmButtonText: 'Ok',
          footer: '<a href="/student/courses/">View Courses</a>'
          })

      }  else {

        Swal.fire({
          title: 'Tutor Marked Assesment',
          text: 'T.M.A Unavailable!!!',
          icon: 'info',
          confirmButtonText: 'Ok'         
          })

      }
      
    }

  } else {

    Swal.fire({
      title: 'Empty Course List',
      text: 'If You Have Registered For The Semester, Go Ahead And Register Your Courses.else Register both Semester And Your Courses',
      icon: 'warning',
      confirmButtonText: 'Ok',
      footer: '<a href="/student/semester/register/">Semester</a><a href="/student/courses/" class="ml-5">Courses</a>'
      })


  }


}

 if ($("#take_tma").length){

  const swalWithBootstrapButtons = Swal.mixin({
      customClass: {
        confirmButton: 'btn btn-success',
        cancelButton: 'btn btn-danger'
      },
      buttonsStyling: false
    })

  const passport_uploaded =  JSON.parse($("#passport_uploaded").text());
  const user_photo = JSON.parse($("#user_photo").text());

  if (passport_uploaded){

  } else {

      Swal.fire({
      title: 'Photo Missing',
      text: 'Upload Your Photo To Take Tma.',
      input: 'file',
      inputAttributes: {
        'accept': 'image/*',
        'aria-label': 'Upload your profile picture'
      },
      imageUrl: user_photo,
      imageWidth: 170,
      imageHeight: 170,
      imageAlt: 'User image',
      showCancelButton: true,
      confirmButtonText: 'Upload',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      showLoaderOnConfirm: true,
      backdrop: false,
      preConfirm: (image) => {
       alert(image);

      $.ajax({
        url:'accounts/upload/photo',
        method: 'POST',
        data: image,
        contentType:false,
        processData:false,
        success: function (response){
          console.log(response);

        if(response.error) {
          alert(response.message);
        } else {
          alert(response.message);
        }
      }

      })
       

      }
    }).then((result) => {
      // if (result.isConfirmed) {

      //   Swal.fire({
      //     title: 'Success!',
      //     text: 'Your photo has been Uploaded.',
      //     icon: 'success',
      //     confirmButtonText: 'Ok',
      //     confirmButtonColor: '#3085d6',
      //     backdrop: false

      // }).then((result) => {
      //     if (result.isConfirmed) {

      //        location.reload()

      //     }
      //   })

      // } else 
      if (
        result.dismiss === Swal.DismissReason.cancel
      ) {

         Swal.fire({
          title: 'Warning',
          text: 'Your Upload Was Canceled.',
          icon: 'warning',
          showCancelButton: true,
          cancelButtonText: 'Ok',
          confirmButtonText: 'Retry',
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonColor: '#3085d6',
          backdrop: false

          }).then((result) => {
          if (result.isConfirmed) {

           location.reload()

          } else if (
        result.dismiss === Swal.DismissReason.cancel
         ) {

         window.location.href = '/student/tma/'

        }

        })

      }
    })

  }

}

if ($("#lecturer_courses").length){

  const lecturer_courses =  JSON.parse($("#lecturer_courses").text());

  if (lecturer_courses < 1 ){

    Swal.fire({
      title: 'Course Unavailable!',
      text: 'It seems you are not assigned any course.Please contact admin to rectify this issue...',
      icon: 'error',
      showConfirmButton: false,
      footer: '<a href="/lecturer/dashboard/">Dashboard</a>',
      backdrop: false

  })

  } 

} 

});


(function ($) {
  "use strict";

  // Add active state to sidbar nav links
  var path = window.location.href; // because the 'href' property of the DOM element is the absolute path
  $("#layoutSidenav_nav .sb-sidenav a.nav-link").each(function () {
    if (this.href === path) {
      $(this).addClass("active");
    }
  });

  // Toggle the side navigation
  $("#sidebarToggle").on("click", function (e) {
    e.preventDefault();
    $("body").toggleClass("sb-sidenav-toggled");
  });


  $("#upload_user_photo").click(function () {

    const swalWithBootstrapButtons = Swal.mixin({
      customClass: {
        confirmButton: 'btn btn-success',
        cancelButton: 'btn btn-danger'
      },
      buttonsStyling: false
    })

    const user_photo = JSON.parse(document.getElementById('user_photo').textContent);

    Swal.fire({
      text: 'Change Photo',
      input: 'file',
      inputAttributes: {
        'accept': 'image/*',
        'aria-label': 'Upload your profile picture'
      },
      imageUrl: user_photo,
      imageWidth: 200,
      imageHeight: 200,
      imageAlt: 'Custom image',
      showCancelButton: true,
      confirmButtonText: 'Upload',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      showLoaderOnConfirm: true,
      preConfirm: (login) => {
        alert('yello');

      //  return fetch(`//api.github.com/users/${login}`)
      //  .then(response => {
      //   if (!response.ok) {
      //     throw new Error(response.statusText)
      //   }
      //   return response.json()
      // })
      // .catch(error => {
      //   Swal.showValidationMessage(
      //     `Request failed: ${error}`
      //   )
      // })

       },
    }).then((result) => {
      if (result.isConfirmed) {
        swalWithBootstrapButtons.fire(
          'Success!',
          'Your photo has been Uploaded.',
          'success'
        )
      } else if (
        result.dismiss === Swal.DismissReason.cancel
      ) {
        swalWithBootstrapButtons.fire(
          'Cancelled',
          'Photo Uploaded Failed!',
          'error'
        )
      }
    })

  });


  $("#reg").click(function () {

    const reg_open = JSON.parse(document.getElementById('reg_open').textContent);
    const sem_reg_status = JSON.parse(document.getElementById('sem_reg_status').textContent);
    const wallet_balance = JSON.parse(document.getElementById('wallet_balance').textContent);
    const reg_check = JSON.parse(document.getElementById('reg_check').textContent);
    const courses = JSON.parse(document.getElementById('courses').textContent);

    if (reg_open) {

      if (sem_reg_status) {

        if (reg_check > 24) {

        Swal.fire({
          title: 'Courses Registered!',
          text: courses,
          icon: 'info',
          confirmButtonText: 'Ok',
          footer: '<a href="/student/courses/">View Courses</a>'
        })

  
        } else {

          if (wallet_balance < 2000) {

            Swal.fire({
              title: 'Insufficient Funds!!!',
              text: 'Your Wallet balance is not enough for this transaction,refund Your Wallet And Try Again',
              icon: 'warning',
              confirmButtonText: 'Ok',
              footer: '<a href="/student/wallet/">Refund Wallet</a>'
            })
    
      
            } else {

              $("#Add_Courses").modal('show');
      
            }       
  
        }


      } else {

        Swal.fire({
          title: 'Semester Unregistered!',
          text: 'Please register for semester to continue courses registration',
          icon: 'warning',
          confirmButtonText: 'Ok',
          footer: '<a href="/student/semester/register/">Register Semester</a>'
        })

      }



    } else {

      Swal.fire({
        title: 'Registration Closed',
        text: 'Course Registration Closed For The Semester.',
        icon: 'error',
        confirmButtonText: 'Ok'
      })

    }

  });


  $("#reg_course").click(function (e) {

    e.preventDefault();

    var link = $(this).attr("href");

    const sem_reg_status = JSON.parse(document.getElementById('sem_reg_status').textContent);

    if (sem_reg_status) {
      
      window.location.href = link;
     
    } else {

      Swal.fire({
        title: 'Semester Unregistered!',
        text: 'Please register for semester to continue courses registration',
        icon: 'warning',
        confirmButtonText: 'Ok',
        footer: '<a href="/student/semester/register/">Register Semester</a>'
      })

    }

  });


  $("#exam_reg").click(function () {

    const course_count = JSON.parse(document.getElementById('course_count').textContent);
    const sem_reg_status = JSON.parse(document.getElementById('sem_reg_status').textContent);

    if (sem_reg_status) {
      
      if (course_count > 0) {
      
        $("#Add_Exam").modal('show');
       
      } else {
      
        Swal.fire({
          title: 'Courses Unregistered!',
          text: 'Sorry, Seems Like You Have No Registered Courses',
          icon: 'error',
          confirmButtonText: 'Ok',
          footer: '<a href="/student/courses/register/">Register Courses</a>'
        })

      }
     
    } else {

      Swal.fire({
        title: 'Semester Unregistered!',
        text: 'Please register for semester to continue courses registration',
        icon: 'warning',
        confirmButtonText: 'Ok',
        footer: '<a href="/student/semester/register/">Register Semester</a>'
      })

    }

  });

})(jQuery);