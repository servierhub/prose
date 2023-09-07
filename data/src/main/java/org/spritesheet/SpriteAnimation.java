package org.spritesheet;

import processing.core.*;

public class SpriteAnimation implements PConstants
{
  public SpriteAnimation(PImage[] data, int frameRate) {
    this.data = data;
    this.frameRate = frameRate;
    this.frameCount = 0;
    rewind();
  }

  public void rewind() {
    this.frame = 0;
  }
  
  public boolean play(float x, float y) {
    if(this.frame < this.data.length) {
      SpriteSheetLibrary.Sketch.image(this.data[this.frame], x, y);
      this.nextFrame();
      return true;
    }
    else {
      return false;
    }
  }
  
  public boolean play(float x, float y, float w, float h) {
    if(this.frame < this.data.length) {
      SpriteSheetLibrary.Sketch.image(this.data[this.frame], x, y, w, h);
      this.nextFrame();
      return true;
    }
    else {
      return false;
    }
  }

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