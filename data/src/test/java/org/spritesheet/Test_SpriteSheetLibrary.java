package org.spritesheet;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

public class Test_SpriteSheetLibrary
{
	@Test
	public void testSpriteSheetLibrary() {
	    PApplet parent = new PApplet();
	    SpriteSheetLibrary spriteSheetLibrary = new SpriteSheetLibrary(parent);
	    assertNotNull(spriteSheetLibrary);
	}
	
	@Test
	public void testSpriteSheetLibraryWithExistingSketch() {
	    PApplet parent = new PApplet();
	    SpriteSheetLibrary.Sketch = parent;
	    SpriteSheetLibrary spriteSheetLibrary = new SpriteSheetLibrary(parent);
	    assertNotNull(spriteSheetLibrary);
	}
	@Test
	public void testLoadSpriteSheet() {
	    // Test case 1
	    String imageFilePath1 = "path/to/image1.png";
	    int spriteWidth1 = 32;
	    int spriteHeight1 = 32;
	    SpriteSheet expected1 = new SpriteSheet(spriteWidth1, spriteHeight1, SpriteSheetLibrary.Sketch.loadImage(imageFilePath1));
	    SpriteSheet actual1 = loadSpriteSheet(imageFilePath1, spriteWidth1, spriteHeight1);
	    assertEquals(expected1, actual1);
	    
	    // Test case 2
	    String imageFilePath2 = "path/to/image2.png";
	    int spriteWidth2 = 64;
	    int spriteHeight2 = 64;
	    SpriteSheet expected2 = new SpriteSheet(spriteWidth2, spriteHeight2, SpriteSheetLibrary.Sketch.loadImage(imageFilePath2));
	    SpriteSheet actual2 = loadSpriteSheet(imageFilePath2, spriteWidth2, spriteHeight2);
	    assertEquals(expected2, actual2);
	    
	    // Test case 3
	    String imageFilePath3 = "path/to/image3.png";
	    int spriteWidth3 = 16;
	    int spriteHeight3 = 16;
	    SpriteSheet expected3 = new SpriteSheet(spriteWidth3, spriteHeight3, SpriteSheetLibrary.Sketch.loadImage(imageFilePath3));
	    SpriteSheet actual3 = loadSpriteSheet(imageFilePath3, spriteWidth3, spriteHeight3);
	    assertEquals(expected3, actual3);
	}
}
