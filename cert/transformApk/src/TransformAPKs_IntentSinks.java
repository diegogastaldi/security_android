import java.util.Iterator;
import java.util.Map;
import soot.Value;
import soot.ArrayType;
import soot.Body;
import soot.BodyTransformer;
import soot.G;
import soot.Hierarchy;
import soot.Local;
import soot.PackManager;
import soot.PatchingChain;
import soot.RefType;
import soot.Scene;
import soot.SootClass;
import soot.SootMethod;
import soot.Transform;
import soot.Type;
import soot.Unit;
import soot.jimple.AbstractStmtSwitch;
import soot.jimple.ArrayRef;
import soot.jimple.IntConstant;
import soot.jimple.InvokeExpr;
import soot.jimple.InvokeStmt;
import soot.jimple.Jimple;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.jimple.internal.AbstractInvokeExpr;
import soot.options.Options;


public class TransformAPKs_IntentSinks {
	static int numSendIntentMethods = 0;
	static String newField = "newField_";
	//public static final String  
	
	public static void main(String[] args) {
		Options.v().set_allow_phantom_refs(true);
		//prefer Android APK files// -src-prec apk
		Options.v().set_src_prec(Options.src_prec_apk);
		//output as APK, too//-f J
		Options.v().set_output_format(Options.output_format_dex);

		// resolve the PrintStream and System soot-classes
		Scene.v().addBasicClass("java.io.PrintStream",SootClass.SIGNATURES);
		Scene.v().addBasicClass("java.lang.System",SootClass.SIGNATURES);

		PackManager.v().getPack("jtp").add(new Transform("jtp.myInstrumenter", new BodyTransformer() {	
			@Override
			protected void internalTransform(final Body b, String phaseName, @SuppressWarnings("rawtypes") Map options) {
				final PatchingChain<Unit> units = b.getUnits();	
				//important to use snapshotIterator here
				for(Iterator<Unit> iter = units.snapshotIterator(); iter.hasNext();) {
					final Unit u = iter.next();
					u.apply(new AbstractStmtSwitch() {
						public void caseInvokeStmt(InvokeStmt stmt) {
							Value val2, val3, arg;
							Type argType;
							Local tmpRef;
							ArrayRef aRef;
							InvokeExpr invokeExpr = stmt.getInvokeExpr();
							/*G.v().out.println("stmt is "+ stmt);*/
							Boolean isIntentSendingMethod = intentSinkMethod(stmt);
							
							if (isIntentSendingMethod == true){
								G.v().out.println("isIntentSendingMethod is " + isIntentSendingMethod);
								if(invokeExpr.getArgCount()>0){
									// If an argument was an intent or array of intents,
									// 1. First need to get the actual intent, from the method call about to make
									// 2. Second need to express something like this, but in jimple 3-register terms: thisIntent.putExtra(tempString, getNumIntents());
									
									//Check if any of the args are android.content.Intent
									for(Iterator arguments = invokeExpr.getArgs().iterator();arguments.hasNext();){
										arg = (Value) arguments.next();
										argType = arg.getType();
										if(argType.toString().contentEquals("android.content.Intent")){
											// Assume only one match of a 'simple intent' (if not in an array), per method call
											incNumIntents();
											String tempString = newField.concat(Integer.toString(getNumIntents()));
											/*G.v().out.println(tempString);
											G.v().out.println("This argument Type MATCHED android.content.Intent");*/
											tmpRef = addTmpRef(b);
											tmpRef = (Local)arg;
											/*G.v().out.println("Local tmpRef " + tmpRef);*/
											SootMethod toCall = Scene.v().getSootClass("android.content.Intent").getMethod("android.content.Intent putExtra(java.lang.String,java.lang.String)");   
											/*G.v().out.print("toCall is " + toCall);*/
											val2 = StringConstant.v(tempString);
											val3 = StringConstant.v(tempString);
											units.insertBefore(Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(tmpRef, toCall.makeRef(),val2, val3)), u);
										} 
										/*else {									
											if (argType instanceof ArrayType) {
												G.v().out.print("IntentsInstrument.java: Argument Type is instance of ArrayType: " + argType);
												if(argType.toString().contentEquals("android.content.Intent[]")){
													//array of intents. putExtra just for item (1)
													incNumIntents();
													String tempString = newField.concat(Integer.toString(getNumIntents()));
													aRef = Jimple.v().newArrayRef(arg, IntConstant.v(1));
													tmpRef = Jimple.v().newLocal(aRef.toString(),RefType.v("android.content.Intent"));
													b.getLocals().add(tmpRef);
													val2 = StringConstant.v(tempString);
													val3 = StringConstant.v(tempString);
													SootMethod toCall = Scene.v().getSootClass("android.content.Intent").getMethod("android.content.Intent putExtra(java.lang.String,java.lang.String)");   
													units.insertBefore(Jimple.v().newInvokeStmt(Jimple.v().newVirtualInvokeExpr(tmpRef, toCall.makeRef(), val2, val3)), u);
													
												}
											}
										}*/
									}

								}
							}
						}
					});
					//check that we did not mess up the Jimple
					b.validate(); 
				}

			}
		}));

		soot.Main.main(args);
	}

	private static Local addTmpRef(Body body)
	{
		Local tmpRef = Jimple.v().newLocal("tmpRef", RefType.v("java.io.PrintStream"));
		body.getLocals().add(tmpRef);
		return tmpRef;
	}
	
	private static Local generateNewLocal(Body body, Type type)
	{		
		Local tmpRef = Jimple.v().newLocal("tmpRef", type);
		body.getLocals().add(tmpRef);
		return tmpRef;
	}

	private static Local addTmpString(Body body)
	{
		Local tmpString = Jimple.v().newLocal("tmpString", RefType.v("java.lang.String")); 
		body.getLocals().add(tmpString);
		return tmpString;
	}

	static int getNumIntents(){
		return numSendIntentMethods;
	}

	static void incNumIntents(){
		numSendIntentMethods++;
	}
	
	public static boolean intentSinkMethod(Stmt stmt) {
		SootClass android_content_Context, android_content_IntentFilter, android_app_Activity;
		boolean isClassSuperOrSameIFILTER, isClassSuperOrSameCONTEXT, isClassSuperOrSameACTIVITY;
		boolean matched = false;
		AbstractInvokeExpr ie = (AbstractInvokeExpr) stmt.getInvokeExpr();
		SootMethod meth = ie.getMethod();
		String methodSubSig = meth.getSubSignature();
		
		/*G.v().out.println("methodSubSig is " + methodSubSig);*/
		if(methodSubSig.contains("void startActivity(android.content.Intent")){
			android_app_Activity = Scene.v().getSootClass("android.app.Activity");	
			isClassSuperOrSameACTIVITY = (new Hierarchy()).isClassSuperclassOfIncluding(android_app_Activity, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: methodSubSig equalled startActivity, and isClassSuperOrSameACTIVITY "+isClassSuperOrSameACTIVITY);
			if(isClassSuperOrSameACTIVITY == true){
				matched = true;
			}
		}
		if(methodSubSig.contains("void startActivityForResult(android.content.Intent,int")){
			android_app_Activity = Scene.v().getSootClass("android.app.Activity");	
			isClassSuperOrSameACTIVITY = (new Hierarchy()).isClassSuperclassOfIncluding(android_app_Activity, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: isClassSuperOrSameACTIVITY "+isClassSuperOrSameACTIVITY);
			if(isClassSuperOrSameACTIVITY == true){
				matched = true;
			}
		}
		if(methodSubSig.contains("void startActivityForResult(android.content.Intent,int,android.os.Bundle")){
			android_app_Activity = Scene.v().getSootClass("android.app.Activity");	
			isClassSuperOrSameACTIVITY = (new Hierarchy()).isClassSuperclassOfIncluding(android_app_Activity, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: isClassSuperOrSameACTIVITY "+isClassSuperOrSameACTIVITY);
			if(isClassSuperOrSameACTIVITY == true){
				matched = true;
			}
		}
		/*if(methodSubSig.contains("void sendBroadcast(android.content.Intent")){
			android_content_Context = Scene.v().getSootClass("android.content.Context");	
			isClassSuperOrSameCONTEXT = (new Hierarchy()).isClassSuperclassOfIncluding(android_content_Context, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: isClassSuperOrSameCONTEXT "+isClassSuperOrSameCONTEXT);
			if(isClassSuperOrSameCONTEXT == true){
				matched = true;
			}
		}
		if(methodSubSig.contains("void sendBroadcast(android.content.Intent,java.lang.String")){
			android_content_Context = Scene.v().getSootClass("android.content.Context");	
			isClassSuperOrSameCONTEXT = (new Hierarchy()).isClassSuperclassOfIncluding(android_content_Context, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: isClassSuperOrSameCONTEXT "+isClassSuperOrSameCONTEXT);
			if(isClassSuperOrSameCONTEXT == true){
				matched = true;
			}
		}	
		//For the addAction method, since no intent or intent array argument, don't currently transform the APK after identifying the method call.
		if(methodSubSig.contains("void addAction(java.lang.String)")){
			android_content_IntentFilter = Scene.v().getSootClass("android.content.IntentFilter");
			isClassSuperOrSameIFILTER = (new Hierarchy()).isClassSuperclassOfIncluding(android_content_IntentFilter, meth.getDeclaringClass());
			//G.v().out.println("intentSinkMethod: isClassSuperOrSameIFILTER "+isClassSuperOrSameIFILTER);
			if(isClassSuperOrSameIFILTER == true){
				matched = true;	
			}
		}*/
		return (matched);
	}
}



