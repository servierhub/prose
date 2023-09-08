package org.spritesheet;

import processing.core.*;

/**
 * The SpriteAnimation class represents an animation made up of a sequence of
 * images. It allows for the creation of a new SpriteAnimation object with the
 * given data and frame rate. The frame counter can be reset to rewind the
 * animation, and images can be displayed at specified coordinates and
 * dimensions. The frame count is incremented and the current frame is updated
 * if the frame count exceeds the frame rate.
 */
public class SpriteAnimation implements PConstants {
    /**
     * Initializes a new SpriteAnimation object with the given data and frame rate.
     *
     * @param data      the array of PImage objects representing the frames of the
     *                  animation
     * @param frameRate the desired frame rate of the animation
     * @return a new SpriteAnimation object
     */
    public SpriteAnimation(PImage[] data, int frameRate) {
        this.data = data;
        this.frameRate = frameRate;
        this.frameCount = 0;
        rewind();
    }

    /**
     * Resets the frame counter to 0, effectively rewinding the current position in
     * the animation.
     */
    public void rewind() {
        this.frame = 0;
    }

    public boolean play(float x, float y) {
        if (this.frame < this.data.length) {
            SpriteSheetLibrary.Sketch.image(this.data[this.frame], x, y);
            this.nextFrame();
            return true;
        } else {
            return false;
        }
    }

    /**
     * Displays an image from the data array at the specified coordinates and
     * dimensions.
     * Increments the frame counter.
     *
     * @param x the x-coordinate of the image's top-left corner
     * @param y the y-coordinate of the image's top-left corner
     * @param w the width of the image
     * @param h the height of the image
     * @return true if the image was successfully displayed, false otherwise
     */
    public boolean play(float x, float y, float w, float h) {
        if (this.frame < this.data.length) {
            SpriteSheetLibrary.Sketch.image(this.data[this.frame], x, y, w, h);
            this.nextFrame();
            return true;
        } else {
            return false;
        }
    }

    /**
     * Increments the frame count and updates the current frame if the frame count
     * exceeds the frame rate.
     */
    private void nextFrame() {
        if (this.frameCount++ >= this.frameRate) {
            this.frameCount = 0;
            this.frame++;
        }
    }

    private int frame;
    private int frameRate;
    private int frameCount;
    private PImage[] data;
}
