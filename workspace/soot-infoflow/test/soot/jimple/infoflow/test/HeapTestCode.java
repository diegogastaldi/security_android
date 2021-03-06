/*******************************************************************************
 * Copyright (c) 2012 Secure Software Engineering Group at EC SPRIDE.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the GNU Lesser Public License v2.1
 * which accompanies this distribution, and is available at
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 * 
 * Contributors: Christian Fritz, Steven Arzt, Siegfried Rasthofer, Eric
 * Bodden, and others.
 ******************************************************************************/
package soot.jimple.infoflow.test;

import java.util.ArrayList;

import soot.jimple.infoflow.test.android.ConnectionManager;
import soot.jimple.infoflow.test.android.TelephonyManager;
import soot.jimple.infoflow.test.utilclasses.ClassWithField;
import soot.jimple.infoflow.test.utilclasses.ClassWithStatic;

public class HeapTestCode {
	
	public class Y{
		String f;
		
		public void set(String s){
			f = s;
		}
	}
	
	public void simpleTest(){
		String taint = TelephonyManager.getDeviceId();
		Y a = new Y();
		Y b = new Y();
		
		a.set(taint);
		b.set("notaint");
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.f);
		
	}
	
	public void argumentTest(){
		ClassWithField x = new ClassWithField();
		run(x);
		x.listField = new ArrayList<String>();
		x.listField.add(TelephonyManager.getDeviceId());
		
	}
	
	public static void run(ClassWithField o){
		o = new ClassWithField();
		o.listField = new ArrayList<String>();
		o.listField.add("empty");
		ConnectionManager cm = new ConnectionManager();
		cm.publish(o.field);
		
	}
	
	public void negativeTest(){
		String taint = TelephonyManager.getDeviceId();
		
		MyArrayList notRelevant = new MyArrayList();
		MyArrayList list = new MyArrayList();
		notRelevant.add(taint);
		list.add("test");
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(list.get());
		
	}
	
	class MyArrayList{
		
		String[] elements;
		
		public void add(String obj){
			if(elements == null){
				elements = new String[3];
			}
			elements[0] = obj;
		}
		
		public String get(){
			return elements[0];
		}
		
	}
	
	public void doubleCallTest(){
		X a = new X();
		X b = new X();
		a.save("neutral");
		b.save(TelephonyManager.getDeviceId());
		ConnectionManager cm = new ConnectionManager();
		cm.publish(String.valueOf(a.e));
	}

	public void methodTest0(){
		String taint = TelephonyManager.getDeviceId();
		X x = new X();
		A a = new A();
		String str = x.xx(a);
		a.b = taint;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(str);
	}
	
	
	class A{
		public String b = "Y";
		public String c = "X";
	}
	
	class X{
		public char[] e;
		public String xx(A o){
			return o.b;
		}
		
		public void save(String f){
			e = f.toCharArray();
		}
	}
	
	
	//########################################################################

	public void methodTest1(){
		String tainted = TelephonyManager.getDeviceId();
		 new AsyncTask().execute(tainted);
	}
	
	protected class AsyncTask{
		public Worker mWorker;
		public FutureTask mFuture;
		
		public AsyncTask(){
			mWorker = new Worker(){
				public void call(){
					ConnectionManager cm = new ConnectionManager();
					cm.publish(mParams);
				}
			};
			mFuture = new FutureTask(mWorker);
		}
		
		public void execute(String t){
			mWorker.mParams = t;
	        //shortcut (no executor used):
			//exec.execute(mFuture);
			mFuture.run();
		}
		
	}
	
	protected class Worker{
		public String mParams;
		
		public void call(){
		}
	}
	protected class FutureTask{
		private final Worker wo;
		public FutureTask(Worker w){
			wo = w;
		}
		public void run(){
			wo.call();
		}
	}
	
	
	//next test:
	
	public void testForWrapper(){
		ConnectionManager cm = new ConnectionManager();
		cm.publish("");
		ClassWithStatic cws = new ClassWithStatic();
		int i = 4+3;
		while(true){
			cws.getTitle();
			if(i ==8){
				break;
			}
		}
		ClassWithStatic.staticString = TelephonyManager.getDeviceId();
	}
	
	
	public void testForLoop(){
		while(true){
			WrapperClass f = new WrapperClass();
			f.sink();
			
			WrapperClass w = new WrapperClass();
			w.callIt();
			
		}
		
	}
	
	public void testForEarlyTermination(){
		ConnectionManager cm = new ConnectionManager();
		cm.publish(ClassWithStatic.staticString);
		
		@SuppressWarnings("unused")
		ClassWithStatic c1 = new ClassWithStatic();
		
		WrapperClass w1 = new WrapperClass();
		
		w1.callIt();
		
	}
	
	class WrapperClass{
		
		public void callIt(){
			ClassWithStatic.staticString = TelephonyManager.getDeviceId();
		}
		
		public void sink(){
			ConnectionManager cm = new ConnectionManager();
			cm.publish(ClassWithStatic.staticString);
		}
		
	}
	
	
	// ----------------- backward flow on return:
	
	public void methodReturn(){
		B b = new B();
		B b2 = b;
		b.attr = m();
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b2.attr.b);
	}
	
	public class B{
		public A attr;
		
		public B() {
			attr = new A();
		}
	}
	
	public A m(){
		A a = new A();
		a.b = TelephonyManager.getDeviceId();
		return a;
		
	}
	
	public void twoLevelTest(){
		SecondLevel l2 = new SecondLevel();
		FirstLevel l1 = new FirstLevel();
		
		String x = l1.getValue(l2, TelephonyManager.getDeviceId());
		String y = l1.getValue(l2, "test");
		x.toString();
		ConnectionManager cm = new ConnectionManager();
		cm.publish(y);
	}
	
	public class FirstLevel{
		
		public String getValue(SecondLevel l, String c){
			return l.id(c);
		}
	}
	
	public class SecondLevel{
		
		public String id(String i){
			return i;
		}
	}
	
	private class DataClass {
		public String data;
		public DataClass next;
	}
	
	public void multiAliasTest() {
		DataClass dc = new DataClass();
		DataClass dc2 = null;
		DataClass dc3 = new DataClass();
		
		dc2 = dc3;
		
		dc2.next = dc;
		
		String a = TelephonyManager.getDeviceId();
		dc.data = a;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(dc3.next.data);
	}	
	
	public void overwriteAliasTest() {
		DataClass dc = new DataClass();
		DataClass dc2 = null;
		DataClass dc3 = new DataClass();
		
		dc2 = dc3;
		
		dc2.next = dc;
		dc3.next = null;
		
		String a = TelephonyManager.getDeviceId();
		dc.data = a;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(dc3.next.data);
	}	

	public void arrayAliasTest() {
		String[] a = new String[1];
		String[] b = a;
		a[0] = TelephonyManager.getDeviceId();
		String[] c = b;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(c[0]);		
	}

	public void functionAliasTest() {
		String tainted = TelephonyManager.getDeviceId();
		DataClass dc1 = new DataClass();
		DataClass dc2 = new DataClass();
		dc1.data = tainted;
		copy(dc1, dc2);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(dc2.data);		
	}

	private void copy(DataClass dc1, DataClass dc2) {
		dc2.data = dc1.data;
	}

	public void functionAliasTest2() {
		DataClass dc1 = new DataClass();
		DataClass dc2 = new DataClass();
		taintMe(dc1);
		copy(dc1, dc2);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(dc2.data);		
	}
	
	public void taintMe(DataClass dc) {
		String tainted = TelephonyManager.getDeviceId();
		dc.data = tainted;
	}
	
	public void multiLevelTaint() {
		String tainted = TelephonyManager.getDeviceId();
		B b = new B();
		A a = b.attr;
		taintLevel1(tainted, b);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a.b);
	}
	
	private void taintLevel1(String data, B b) {
		taintLevel2(data, b.attr);
	}

	private void taintLevel2(String data, A a) {
		a.b = data;
	}

	public void negativeMultiLevelTaint() {
		String tainted = TelephonyManager.getDeviceId();
		B b = new B();
		A a = b.attr;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a.b);
		taintLevel1(tainted, b);
	}

	public void negativeMultiLevelTaint2() {
		String tainted = TelephonyManager.getDeviceId();
		B b = new B();
		taintLevel1b(tainted, b);
	}

	private void taintLevel1b(String data, B b) {
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
		taintLevel2(data, b.attr);
	}

	public void multiLevelTaint2() {
		String tainted = TelephonyManager.getDeviceId();
		B b = new B();
		taintLevel1c(tainted, b);
	}

	private void taintLevel1c(String data, B b) {
		taintLevel2(data, b.attr);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
	}
	
	public void threeLevelTest() {
		B b = new B();
		A a = b.attr;
		taintOnNextLevel(b, a);
	}
	
	private void taintMe(B b) {
		b.attr.b = TelephonyManager.getDeviceId();
	}
	
	private void taintOnNextLevel(B b, A a) {
		taintMe(b);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a.b);		
	}
	
	private class RecursiveDataClass {
		RecursiveDataClass child;
		String data;

		public void leakIt() {
			ConnectionManager cm = new ConnectionManager();
			cm.publish(data);
			if (child != null)
				child.leakIt();
		}
	}
	
	public void recursionTest() {
		RecursiveDataClass rdc = new RecursiveDataClass();
		rdc.data = TelephonyManager.getDeviceId();
		rdc.leakIt();
	}

	public void activationUnitTest1() {
		B b = new B();
		
		A a = b.attr;
		String tainted = TelephonyManager.getDeviceId();
		a.b = tainted;

		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
	}
	
	public void activationUnitTest2() {
		B b = new B();
		b.attr = new A();
		
		A a = b.attr;
		String tainted = TelephonyManager.getDeviceId();

		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);

		a.b = tainted;
	}

	public void activationUnitTest3() {
		B b = new B();
		b.attr = new A();
		
		B b2 = new B();
		b2.attr = new A();

		String tainted = TelephonyManager.getDeviceId();
		
		b.attr.b = tainted;	
		b2.attr.b = b.attr.b;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b2.attr.b);
	}

	public void activationUnitTest4() {
		B b = new B();
		b.attr = new A();
		
		B b2 = new B();
		b2.attr = new A();

		String tainted = TelephonyManager.getDeviceId();
		
		b2.attr.b = tainted;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);

		b.attr.b = tainted;
	}

	public void activationUnitTest4b() {
		B b = new B();
		b.attr = new A();
		
		B b2 = new B();
		b2.attr = new A();

		String tainted = TelephonyManager.getDeviceId();
		
		b2.attr.b = tainted;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);

		b.attr = b2.attr;
	}

	public void activationUnitTest5() {
		B b = new B();
		b.attr = new A();
		
		B b2 = new B();
		b2.attr = new A();

		ConnectionManager cm = new ConnectionManager();
		String tainted = TelephonyManager.getDeviceId();
		
		cm.publish(b.attr.b);
		cm.publish(b2.attr.b);

		b.attr = b2.attr;
		
		cm.publish(b.attr.b);
		cm.publish(b2.attr.b);

		b.attr.b = tainted;
	}
	
	public void returnAliasTest() {
		String tainted = TelephonyManager.getDeviceId();
		B b = new B();
		B c = b;
		A a = alias(c);
		c.attr.b = tainted;
		b.attr.b = tainted;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a.b);
	}
	
	private A alias(B b) {
		return b.attr;
	}
	
	public void callPerformanceTest() {
		A a = new A();
		a.b = getDeviceId();
		B b = new B();
		b.attr = a;

		doIt(b);
	}
	
	private void doIt(B b) {
		throwAround(b);
		System.out.println(b.attr.b);
	}

	private String getDeviceId() {
		String tainted = TelephonyManager.getDeviceId();
		return tainted;
	}

	private void throwAround(B b) {
		throwAround2(b.attr);
	}
	
	private void throwAround2(A a) {
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a.b);
	}
	
	private B b1;
	private B b2;
	
	private void foo(B b1, B b2) {
		this.b1 = b1;
		this.b2 = b2;
	}

	@SuppressWarnings("unused")
	private void foo2(B b1, B b2) {
		//
	}
	
	private A bar(A a) {
		this.b1.attr = a;
		return this.b2.attr;
	}

	@SuppressWarnings("unused")
	private A bar2(A a) {
		return null;
	}
	
	public void testAliases() {
		B b = new B();
		A a = new A();
		a.b = TelephonyManager.getDeviceId();
		
		// Create the alias
		foo(b, b);
		String tainted = bar(a).b;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(tainted);
	}

	public void testWrapperAliases() {
		B b = new B();
		A a = new A();
		a.b = TelephonyManager.getDeviceId();
		
		// Create the alias
		foo2(b, b);
		String tainted = bar2(a).b;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(tainted);
	}

	public void negativeTestAliases() {
		B b = new B();
		A a = new A();
		a.b = TelephonyManager.getDeviceId();
		
		// Create the alias
		foo(b, b);
		String untainted = bar(a).c;
		
		ConnectionManager cm = new ConnectionManager();
		cm.publish(untainted);
	}
	
	private void alias(B b1, B b2) {
		b2.attr = b1.attr;
	}
	
	private void set(B a, String secret, B b) {
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
		a.attr.b = secret;
		cm.publish(b.attr.b);
	}
	
	private void foo(B a) {
		System.out.println(a);
	}
	
	public void aliasPerformanceTest() {
		B a = new B();
		B b = new B();
		alias(a, b);
		set(a, TelephonyManager.getDeviceId(), b);
		foo(a);
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
	}
	
	public void backwardsParameterTest() {
		B b1 = new B();
		b1.attr = new A();
		B b2 = new B();
		
		alias(b1, b2);
		
		b2.attr.b = TelephonyManager.getDeviceId();
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b1.attr.b);
	}
	
	public void aliasTaintLeakTaintTest() {
		B b = new B();
		b.attr = new A();
		A a = b.attr;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.attr.b);
		b.attr.b = TelephonyManager.getDeviceId();
		cm.publish(a.b);
	}
	
	public void fieldBaseOverwriteTest() {
		A a = new A();
		a.b = TelephonyManager.getDeviceId();
		A a2 = a;
		ConnectionManager cm = new ConnectionManager();
		cm.publish(a2.b);
	}
	
	private A alias(A a) {
		return a;
	}
	
	public void doubleAliasTest() {
		A a = new A();
		A b = alias(a);
		A c = alias(a);
		a.b = TelephonyManager.getDeviceId();
		ConnectionManager cm = new ConnectionManager();
		cm.publish(b.b);
		cm.publish(c.b);
	}
	
	private int intData;
	
	private void setIntData() {
		this.intData = TelephonyManager.getIMEI();
	}
	
	public void intAliasTest() {
		setIntData();
		ConnectionManager cm = new ConnectionManager();
		cm.publish(intData);
	}

}
