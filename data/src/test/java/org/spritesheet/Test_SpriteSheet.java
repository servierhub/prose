package org.spritesheet;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

public class Test_SpriteSheet
{
	@Test
	public void testConstructor() {
	    int spriteWidth = 10;
	    int spriteHeight = 20;
	    PImage data = new PImage();
	    
	    SpriteSheet spriteSheet = new SpriteSheet(spriteWidth, spriteHeight, data);
	    
	    assertEquals(spriteWidth, spriteSheet.getSpriteWidth());
	    assertEquals(spriteHeight, spriteSheet.getSpriteHeight());
	    assertEquals(data, spriteSheet.getData());
	}
	@Test
	public void testGetAnimation() {
	    // Test case 1
	    int startFrame1 = 0;
	    int numFrames1 = 3;
	    int frameRate1 = 30;
	    SpriteAnimation expectedAnimation1 = new SpriteAnimation(new PImage[]{}, 30);
	    SpriteAnimation actualAnimation1 = getAnimation(startFrame1, numFrames1, frameRate1);
	    assertArrayEquals(expectedAnimation1.getFrames(), actualAnimation1.getFrames());
	    assertEquals(expectedAnimation1.getFrameRate(), actualAnimation1.getFrameRate());
	
	    // Test case 2
	    int startFrame2 = 5;
	    int numFrames2 = 4;
	    int frameRate2 = 60;
	    SpriteAnimation expectedAnimation2 = new SpriteAnimation(new PImage[]{}, 60);
	    SpriteAnimation actualAnimation2 = getAnimation(startFrame2, numFrames2, frameRate2);
	    assertArrayEquals(expectedAnimation2.getFrames(), actualAnimation2.getFrames());
	    assertEquals(expectedAnimation2.getFrameRate(), actualAnimation2.getFrameRate());
	
	    // Test case 3
	    int startFrame3 = 10;
	    int numFrames3 = 2;
	    int frameRate3 = 15;
	    SpriteAnimation expectedAnimation3 = new SpriteAnimation(new PImage[]{}, 15);
	    SpriteAnimation actualAnimation3 = getAnimation(startFrame3, numFrames3, frameRate3);
	    assertArrayEquals(expectedAnimation3.getFrames(), actualAnimation3.getFrames());
	    assertEquals(expectedAnimation3.getFrameRate(), actualAnimation3.getFrameRate());
	}
	@Test
	public void testGetImage() {
	    // Create a mock PImage object
	    PImage mockImage = Mockito.mock(PImage.class);
	    
	    // Create a mock PImage object for data
	    PImage mockData = Mockito.mock(PImage.class);
	    
	    // Set the width and height of the mock data
	    int dataWidth = 100;
	    int dataHeight = 100;
	    Mockito.when(mockData.width).thenReturn(dataWidth);
	    Mockito.when(mockData.height).thenReturn(dataHeight);
	    
	    // Set the sprite width and height
	    int spriteWidth = 10;
	    int spriteHeight = 10;
	    
	    // Create an instance of the class under test
	    YourClass yourClass = new YourClass(mockData, spriteWidth, spriteHeight);
	    
	    // Test case 1: frame = 0
	    int frame1 = 0;
	    int expectedX1 = 0;
	    int expectedY1 = 0;
	    Mockito.when(mockData.get(expectedX1 * spriteWidth, expectedY1 * spriteHeight, spriteWidth, spriteHeight)).thenReturn(mockImage);
	    PImage result1 = yourClass.getImage(frame1);
	    assertEquals(mockImage, result1);
	    
	    // Test case 2: frame = 5
	    int frame2 = 5;
	    int expectedX2 = 5;
	    int expectedY2 = 0;
	    Mockito.when(mockData.get(expectedX2 * spriteWidth, expectedY2 * spriteHeight, spriteWidth, spriteHeight)).thenReturn(mockImage);
	    PImage result2 = yourClass.getImage(frame2);
	    assertEquals(mockImage, result2);
	    
	    // Test case 3: frame = 10
	    int frame3 = 10;
	    int expectedX3 = 0;
	    int expectedY3 = 1;
	    Mockito.when(mockData.get(expectedX3 * spriteWidth, expectedY3 * spriteHeight, spriteWidth, spriteHeight)).thenReturn(mockImage);
	    PImage result3 = yourClass.getImage(frame3);
	    assertEquals(mockImage, result3);
	}
	@Test
	public void testHello() {
	    ByteArrayOutputStream outContent = new ByteArrayOutputStream();
	    System.setOut(new PrintStream(outContent));
	    
	    hello();
	    
	    assertEquals("Hello the world\n", outContent.toString());
	}
}
