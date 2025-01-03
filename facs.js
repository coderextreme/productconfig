"use strict";
var fs = require('fs');
var path = require('path');

var def_prefixes = ["Lower_teeth", "Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"];

function getBlueColor() {
    return new SFColor(0.0, 0.0, 1.0);
}

function getGreenColor() {
    return new SFColor(0.0, 1.0, 0.0);
}

function getBlackColor() {
    return new SFColor(0.0, 0.0, 0.0);
}

function readNestedFileSystem(dirPath, startsWith, ext) {
  var files = fs.readdirSync(dirPath);
  var result = [];

  files.forEach(file => {
    var filePath = path.join(dirPath, file);
    var stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      result.push(...readNestedFileSystem(filePath, startsWith, ext));
    } else {
      var fileExt = path.extname(file);
      if (fileExt.toLowerCase() === ext && file.startsWith(startsWith)) {
      	result.push(filePath);
      }
    }
  });

  return result;
}

function generateShapes(targetDirectory, targetStart, targetExtension) {
    var shapeContainer = Browser.currentScene.getNamedNode('shapeContainer');
    var files = readNestedFileSystem(targetDirectory, targetStart, targetExtension);

    for (var bodyPart = 0; bodyPart <= def_prefixes.length; bodyPart++) {
	    for (var i = 0; i < files.length; i++) {
		var file = files[i].replaceAll('\\','/');
	

		var blueshape = Browser.currentScene.createNode('Shape');
		var bluegeometry = Browser.currentScene.createNode('Rectangle2D');
		bluegeometry.size = new SFVec2f(2.5, 2.5);
		var blueappearance = Browser.currentScene.createNode('Appearance');
		var bluematerial = Browser.currentScene.createNode('Material');
		bluematerial.diffuseColor = getBlueColor();
		blueappearance.material = bluematerial;
		blueshape.geometry = bluegeometry;
		blueshape.appearance = blueappearance;

		var greenshape = Browser.currentScene.createNode('Shape');
		var greengeometry = Browser.currentScene.createNode('Rectangle2D');
		greengeometry.size = new SFVec2f(2.5, 2.5);
		var greenappearance = Browser.currentScene.createNode('Appearance');
		var greenmaterial = Browser.currentScene.createNode('Material');
		greenmaterial.diffuseColor = getGreenColor();
		greenappearance.material = greenmaterial;
		greenshape.geometry = greengeometry;
		greenshape.appearance = greenappearance;

		var switch1 = Browser.currentScene.createNode('Switch');
		switch1.children = new MFNode(blueshape, greenshape);
		switch1.whichChoice = 0;


		var transform = Browser.currentScene.createNode('Transform');
		transform.translation.x = i - files.length / 2;
		transform.translation.y = bodyPart - def_prefixes.length / 2;
		/*
		if (transform.translation.x % 2 == 0) {
			transform.translation.y -= 0.43;
		}
		*/
		transform.translation.z = 0;
		transform.scale.x = 0.30;
		transform.scale.y = 0.30;
		transform.scale.z = 0.30;

		var touchSensor = Browser.currentScene.createNode('TouchSensor');
		var booleanTrigger = Browser.currentScene.createNode('BooleanTrigger');
		var integerSequencer = Browser.currentScene.createNode('IntegerSequencer');
		integerSequencer.key = new MFInt32(0, 1);
		integerSequencer.keyValue = new MFInt32(1, 0);

	        var basename = file.replace(/.*\//, "");
		if (bodyPart == def_prefixes.length) {
			var description = basename.substring(3, basename.length-4)+" All Body Parts";
		} else {
			var description = basename.substring(3, basename.length-4)+" "+def_prefixes[bodyPart];
		}
		touchSensor.description = description;

		var DEF = description.replaceAll(" ", "");
		Browser.currentScene.addNamedNode(DEF, touchSensor);
		Browser.currentScene.addNamedNode(DEF+"Switch", switch1);
		Browser.currentScene.addNamedNode(DEF+"IntegerSequencer", integerSequencer);
		Browser.currentScene.addNamedNode(DEF+"BooleanTrigger", booleanTrigger);

		transform.children.push(touchSensor);
		transform.children.push(switch1);
		transform.children.push(integerSequencer);
		transform.children.push(booleanTrigger);

		var touchRoute = Browser.addRoute(touchSensor, "touchTime",  booleanTrigger, "set_triggerTime")
		var triggerRoute = Browser.addRoute(booleanTrigger, "triggerTrue", integerSequencer, "next")
		var sequencerRoute = Browser.addRoute(integerSequencer, "value_changed",  switch1, "whichChoice")

		shapeContainer.children.push(transform);
	}

	var textshape = Browser.currentScene.createNode('Shape');
	var textgeometry = Browser.currentScene.createNode('Text');
	var fontStyle = Browser.currentScene.createNode('FontStyle');
	if (bodyPart == def_prefixes.length) {
		textgeometry.string = "All Body Parts";
	} else {
		textgeometry.string = def_prefixes[bodyPart];
	}

	fontStyle.size = 1.0;
	fontStyle.spacing = 1.2;
	fontStyle.horizontal = false;
        textgeometry.fontStyle = fontStyle;

	var textappearance = Browser.currentScene.createNode('Appearance');
	var textmaterial = Browser.currentScene.createNode('Material');
	textmaterial.diffuseColor = getBlackColor();
	textappearance.material = textmaterial;
	textshape.geometry = textgeometry;
	textshape.appearance = textappearance;

	var texttransform = Browser.currentScene.createNode('Transform');
	texttransform.translation.x = files.length - files.length / 2;
	texttransform.translation.y = bodyPart - def_prefixes.length / 2 + 0.5;
	texttransform.children.push(textshape);
	shapeContainer.children.push(texttransform);
    }
    var xml = Browser.currentScene.toXMLString();
    console.log(xml);
    // fs.writeFileSync("FACSApp.x3d", xml);
}
function initialize() {
    var targetDirectory = 'C:/Users/jcarl/ci2had/resources/';
    var targetStart = 'Jin';
    var targetExtension = '.x3d';
    generateShapes(targetDirectory, targetStart, targetExtension);
}
