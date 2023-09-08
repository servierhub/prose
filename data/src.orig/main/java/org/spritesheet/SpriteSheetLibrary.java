package org.spritesheet;

import processing.core.*;

public class SpriteSheetLibrary
{
    public static PApplet Sketch = null;

	public SpriteSheetLibrary(PApplet parent) {
		if(SpriteSheetLibrary.Sketch == null) {
			SpriteSheetLibrary.Sketch = parent;
		}
	}

	public SpriteSheet loadSpriteSheet(String imageFilePath, int spriteWidth, int spriteHeight) {
		return new SpriteSheet(spriteWidth, spriteHeight, SpriteSheetLibrary.Sketch.loadImage(imageFilePath));
	}
}
