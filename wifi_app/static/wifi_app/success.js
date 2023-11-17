window.onload = function () {
  setTimeout(function () {
    fetch("/shutdown_hotspot/");
  }, 6000);
};
