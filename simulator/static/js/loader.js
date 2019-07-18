function showLoading(component) {
    $("." + component+" .loading-component").css("visibility", "visible");
}

function hideLoading(component) {
    $("." + component +" .loading-component").css("visibility", "hidden");
}