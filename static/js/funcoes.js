function autoComplete(inputSelector) {
    var inputElement = $(inputSelector);
    var buscaUrl = inputElement.data('url');
    var hiddenSelector = inputElement.data('hidden');

    $(inputSelector).autocomplete({
        source: function(request, response) {
            $.ajax({
                url: buscaUrl,
                dataType: "json",
                data: {
                    q: request.term
                },
                success: function(data) {
                    // CORREÇÃO AQUI: 
                    // O Python já manda 'label' e 'value', então usamos eles diretamente.
                    response($.map(data, function(item) {
                        return {
                            label: item.label, // Antes estava item.nome
                            value: item.value, // Antes estava item.nome
                            id: item.id
                        };
                    }));
                }
            });
        },
        select: function(event, ui) {
            $(hiddenSelector).val(ui.item.id);
        }
    });
}


        // Função para carregar a imagem no canvas
        function loadImage(base64Image,target_canvas) {

            var img = new Image();
            img.src = base64Image;
           

            img.onload = function() {
                const canvas = document.getElementById(target_canvas);
                const ctx = canvas.getContext('2d');
                var canvasWidth = canvas.width;
                var canvasHeight = canvas.height;
    
                // Dimensões da imagem original
                var imgWidth = img.width;
                var imgHeight = img.height;

                // Calcula a proporção para redimensionamento
                var scaleWidth = canvasWidth / imgWidth;
                var scaleHeight = canvasHeight / imgHeight;
                var scale = Math.min(scaleWidth, scaleHeight); // Mantém a proporção

                // Novas dimensões da imagem
                var newWidth = imgWidth * scale;
                var newHeight = imgHeight * scale;

                // Calcula a posição para centralizar a imagem no canvas
                var offsetX = (canvasWidth - newWidth) / 2;
                var offsetY = (canvasHeight - newHeight) / 2; 

                // Limpa o canvas e desenha a imagem redimensionada
                ctx.clearRect(0, 0, canvasWidth, canvasHeight);
                ctx.drawImage(img, offsetX, offsetY, newWidth, newHeight);
            };

        }