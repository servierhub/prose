package org.spritesheet;

import processing.core.*;

/**
 * Initializes a new instance of the SpriteSheetLibrary class.
 */
public class SpriteSheetLibrary {
    public static PApplet Sketch = null;

    /**
     * Initializes a new instance of the SpriteSheetLibrary class.
     *
     * This method assigns the provided PApplet object to the Sketch variable if it
     * is null.
     *
     * @param parent the PApplet object to assign to the Sketch variable
     */
    public SpriteSheetLibrary(PApplet parent) {
        if (SpriteSheetLibrary.Sketch == null) {
            SpriteSheetLibrary.Sketch = parent;
        }
    }

    /**
     * Loads a sprite sheet from an image file.
     *
     * This method creates a new SpriteSheet object using the specified sprite width
     * and height, and loads the image file from the given file path using the
     * Sketch.loadImage() method from the SpriteSheetLibrary class.
     *
     * @param imageFilePath the file path of the image file to load
     * @param spriteWidth   the width of each sprite in the sprite sheet
     * @param spriteHeight  the height of each sprite in the sprite sheet
     * @return a new SpriteSheet object with the specified sprite width, height, and
     *         loaded image
     */
    public SpriteSheet loadSpriteSheet(String imageFilePath, int spriteWidth, int spriteHeight) {
        return new SpriteSheet(spriteWidth, spriteHeight, SpriteSheetLibrary.Sketch.loadImage(imageFilePath));
    }
}
