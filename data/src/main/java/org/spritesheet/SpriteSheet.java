package org.spritesheet;

import processing.core.*;

	/**
	 * The SpriteSheet class represents a sprite sheet, which is a single image that contains multiple frames of animation.
	 * It allows for the extraction of individual frames from the sprite sheet and the creation of sprite animations.
	 * 
	 * To create a new SpriteSheet object, the sprite width, sprite height, and image data representing the sprite sheet must be provided.
	 * 
	 * Note: This class requires the Processing library to be imported.
	 */
public class SpriteSheet {

	/**
	 * Creates a new SpriteSheet object with the specified sprite width, sprite height, and image data.
	 * 
	 * @param spriteWidth the width of each sprite in the sprite sheet
	 * @param spriteHeight the height of each sprite in the sprite sheet
	 * @param data the image data representing the sprite sheet
	 */
    protected SpriteSheet(int spriteWidth, int spriteHeight, PImage data) {
        this.spriteWidth = spriteWidth;
        this.spriteHeight = spriteHeight;
        this.data = data;
    }

	/**
	 * Returns a SpriteAnimation object based on the given parameters.
	 * 
	 * This method creates an array of PImage frames based on the startFrame, numFrames, and frameRate parameters.
	 * It calculates the x and y coordinates of each frame within the sprite sheet using the spriteWidth and spriteHeight properties.
	 * The frames are then extracted from the sprite sheet using the get() method of the PImage data object.
	 * Finally, a new SpriteAnimation object is created using the frames array and frameRate, and returned.
	 * 
	 * @param startFrame the index of the first frame in the sprite sheet
	 * @param numFrames the number of frames to extract from the sprite sheet
	 * @param frameRate the frame rate at which the animation should play
	 * @return a SpriteAnimation object representing the extracted frames from the sprite sheet
	 */
    public SpriteAnimation getAnimation(int startFrame, int numFrames, int frameRate) {
        PImage[] frames = new PImage[numFrames];
        for (int j = 0; j < numFrames; j++) {
            int x = (startFrame + j) % (this.data.width / this.spriteWidth);
            int y = (startFrame + j) / (this.data.width / this.spriteWidth);
            frames[j] = this.data.get(x * this.spriteWidth, y * this.spriteHeight, this.spriteWidth, this.spriteHeight);
        }
        return new SpriteAnimation(frames, frameRate);
    }

	/**
	 * Returns an image from the data based on the given frame number.
	 * 
	 * @param frame the frame number to retrieve the image from
	 * @return the image corresponding to the given frame number
	 */
    public PImage getImage(int frame) {
        int x = frame % (this.data.width / this.spriteWidth);
        int y = frame / (this.data.width / this.spriteWidth);
        return this.data.get(x * this.spriteWidth, y * this.spriteHeight, this.spriteWidth, this.spriteHeight);
    }

	/**
	 * Prints "Hello the world" to the console.
	 */
    public void hello() {
        System.out.println("Hello the world");
    }

    private int spriteWidth;
    private int spriteHeight;
    private PImage data;
}
