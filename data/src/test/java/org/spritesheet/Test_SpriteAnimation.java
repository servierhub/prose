package org.spritesheet;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

public class Test_SpriteAnimation
{
	@Test
	public void testSpriteAnimation() {
	    PImage[] data = new PImage[3];
	    data[0] = new PImage();
	    data[1] = new PImage();
	    data[2] = new PImage();
	    int frameRate = 30;
	    
	    SpriteAnimation spriteAnimation = new SpriteAnimation(data, frameRate);
	    
	    assertEquals(data, spriteAnimation.getData());
	    assertEquals(frameRate, spriteAnimation.getFrameRate());
	    assertEquals(0, spriteAnimation.getFrameCount());
	}
	@Test
	public void testRewind() {
	    // Create an instance of the class
	    ClassName obj = new ClassName();
	
	    // Set the frame to a non-zero value
	    obj.setFrame(5);
	
	    // Call the rewind method
	    obj.rewind();
	
	    // Check if the frame is set to 0
	    assertEquals(0, obj.getFrame());
	}
	
	@Test
	public void testRewindWithNegativeFrame() {
	    // Create an instance of the class
	    ClassName obj = new ClassName();
	
	    // Set the frame to a negative value
	    obj.setFrame(-5);
	
	    // Call the rewind method
	    obj.rewind();
	
	    // Check if the frame is set to 0
	    assertEquals(0, obj.getFrame());
	}
	
	@Test
	public void testRewindWithZeroFrame() {
	    // Create an instance of the class
	    ClassName obj = new ClassName();
	
	    // Set the frame to 0
	    obj.setFrame(0);
	
	    // Call the rewind method
	    obj.rewind();
	
	    // Check if the frame is set to 0
	    assertEquals(0, obj.getFrame());
	}
	@Test
	public void testPlayReturnsTrueWhenFrameIsLessThanDataLength() {
	    // Arrange
	    float x = 0.0f;
	    float y = 0.0f;
	    float w = 100.0f;
	    float h = 100.0f;
	    int frame = 0;
	    PImage[] data = new PImage[3];
	    data[0] = new PImage();
	    data[1] = new PImage();
	    data[2] = new PImage();
	    SpriteSheetLibrary.Sketch = new Sketch();
	    SpriteSheetLibrary.Sketch.frame = frame;
	    SpriteSheetLibrary.Sketch.data = data;
	
	    // Act
	    boolean result = SpriteSheetLibrary.Sketch.play(x, y, w, h);
	
	    // Assert
	    assertTrue(result);
	}
	
	@Test
	public void testPlayReturnsFalseWhenFrameIsEqualToDataLength() {
	    // Arrange
	    float x = 0.0f;
	    float y = 0.0f;
	    float w = 100.0f;
	    float h = 100.0f;
	    int frame = 3;
	    PImage[] data = new PImage[3];
	    data[0] = new PImage();
	    data[1] = new PImage();
	    data[2] = new PImage();
	    SpriteSheetLibrary.Sketch = new Sketch();
	    SpriteSheetLibrary.Sketch.frame = frame;
	    SpriteSheetLibrary.Sketch.data = data;
	
	    // Act
	    boolean result = SpriteSheetLibrary.Sketch.play(x, y, w, h);
	
	    // Assert
	    assertFalse(result);
	}
	@Test
	public void testNextFrame_frameCountLessThanFrameRate() {
	    // Arrange
	    int initialFrameCount = 0;
	    int initialFrameRate = 10;
	    int initialFrame = 0;
	    
	    // Act
	    nextFrame();
	    
	    // Assert
	    assertEquals(initialFrameCount + 1, frameCount);
	    assertEquals(initialFrameRate, frameRate);
	    assertEquals(initialFrame, frame);
	}
	
	@Test
	public void testNextFrame_frameCountEqualToFrameRate() {
	    // Arrange
	    int initialFrameCount = 9;
	    int initialFrameRate = 10;
	    int initialFrame = 0;
	    
	    // Act
	    nextFrame();
	    
	    // Assert
	    assertEquals(0, frameCount);
	    assertEquals(initialFrameRate, frameRate);
	    assertEquals(initialFrame + 1, frame);
	}
	
	@Test
	public void testNextFrame_frameCountGreaterThanFrameRate() {
	    // Arrange
	    int initialFrameCount = 10;
	    int initialFrameRate = 10;
	    int initialFrame = 0;
	    
	    // Act
	    nextFrame();
	    
	    // Assert
	    assertEquals(0, frameCount);
	    assertEquals(initialFrameRate, frameRate);
	    assertEquals(initialFrame + 1, frame);
	}
}
