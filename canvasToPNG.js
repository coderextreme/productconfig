"use strict";

const fs = require("fs");

async function canvasToPNG(output) {
   const
      canvas   = document .getElementByTagName ("canvas"),
      Browser  = canvas .browser,
      width    = 1280,
      height   = 720,
      mimeType = "image/png";

   Browser .setBrowserOption ("PrimitiveQuality", "HIGH");
   Browser .setBrowserOption ("TextureQuality",   "HIGH");

   await Browser .resize (width, height);
   const blob = await generateImage (canvas, mimeType, 1);

   fs .writeFileSync (output, new DataView (await blob .arrayBuffer ()));
}

async function generateImage (canvas, mimeType, quality)
{
   return new Promise ((resolve, reject) =>
   {
      canvas .toBlob (blob => resolve (blob), mimeType, quality);
   });
}

module.exports = canvasToPNG;
