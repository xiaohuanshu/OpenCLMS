function drawRotated(img, operater, fullwidth) {
    var degrees = img.data('degrees');
    if (typeof(degrees) === "undefined") {
        degrees = 0;
    }
    if (operater === 'right') {
        degrees += 90;
    } else {
        if (degrees === 0)
            degrees = 270;
        else
            degrees -= 90;
    }
    degrees = degrees % 360;
    img.data('degrees', degrees);
    if (typeof(img.next()[0]) !== "undefined" && img.next()[0].tagName === 'CANVAS') {
        img.next().remove();
    }

    var canvas = document.createElement("canvas");
    var image = new Image();
    image.src = img[0].src;
    var ctx = canvas.getContext("2d");
    if (fullwidth) {
        $(canvas).width("100%");
    } else {
        $(canvas).css({"max-width": "100%"});
    }
    if (degrees === 90 || degrees === 270) {
        canvas.width = image.height;
        canvas.height = image.width;
    } else {
        canvas.width = image.width;
        canvas.height = image.height;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (degrees == 90 || degrees == 270) {
        ctx.translate(image.height / 2, image.width / 2);
    } else {
        ctx.translate(image.width / 2, image.height / 2);
    }
    ctx.rotate(degrees * Math.PI / 180);
    ctx.drawImage(image, -image.width / 2, -image.height / 2);
    img.after(canvas);
    img.hide();
}