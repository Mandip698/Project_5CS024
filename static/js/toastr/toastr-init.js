function DisplayNotification(type, msg) {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "positionClass": "toast-bottom-right",
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Display according to Message Type
    if (type == "success") {
        toastr.success(msg);
    }
    else if (type == "error") {
        toastr.error(msg);
    }
    else if (type == "warning") {
        toastr.warning(msg);
    }
    else {
        toastr.info(msg);
    }
}
