package com.example.intentleak;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.Writer;

import android.os.Bundle;
import android.app.Activity;
import android.content.Intent;
import android.view.Menu;

public class MainActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		Intent i = this.getIntent();	// we want this to be marked as the Source
		int x = 1;
		x = i.getFlags();   // FlowDroid considers getFlags() as a Source method
		int y = 5;		// NOT relevant to the tainted flow Path
		y = x/2;		// relevant
		int z = 1;		// NOT relevant to the Tainted flow
		Writer writer = new PrintWriter(System.out);
		try {
			writer.write(x);	// relevant
			writer.write(z);	// NOT relevant
			sendDataToSink(y);	// relevant method call
			writer.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
		setContentView(R.layout.activity_main);
	}
	
	public void sendDataToSink(int a){
		Writer writer = new PrintWriter(System.out);
		try {
			writer.write(a);	// Sink
			writer.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

}
