package org.spritesheet;

import processing.core.*;

public class SpriteSheet
{
	protected SpriteSheet(int spriteWidth, int spriteHeight, PImage data) {
		this.spriteWidth = spriteWidth;
		this.spriteHeight = spriteHeight;
		this.data = data;
	}

	public SpriteAnimation getAnimation(int startFrame, int numFrames, int frameRate) {
		PImage[] frames = new PImage[numFrames];
		for(int j = 0; j < numFrames; j++) {
			int x = (startFrame + j ) % (this.data.width / this.spriteWidth);
			int y = (startFrame + j) / (this.data.width / this.spriteWidth);
			frames[j] = this.data.get(x * this.spriteWidth, y * this.spriteHeight, this.spriteWidth, this.spriteHeight);
		}
		return new SpriteAnimation(frames, frameRate);
	}

	public PImage getImage(int frame) {
		int x = frame % (this.data.width / this.spriteWidth);
		int y = frame / (this.data.width / this.spriteWidth);
		return this.data.get(x * this.spriteWidth, y * this.spriteHeight, this.spriteWidth, this.spriteHeight);
	}

	private int spriteWidth;
	private int spriteHeight;
	private PImage data;
}