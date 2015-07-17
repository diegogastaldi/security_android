                                // Generate glue code

import java.io.*;
import java.util.*;

class typeinfo
{
  String scm_name;
  String java_name;
  String java_inp_type[];

  typeinfo(String sname, String jname, String jit[])
  {
    scm_name = sname;
    java_name = jname;
    java_inp_type = jit;
  }

  void write(PrintStream out)
  {
    int mode;

    out.println("//Autogenerated by typeinfo on " + new Date());

    out.println("class scm" + java_name + " extends Procedure implements Obj");
    out.println("{");
    out.println("  Obj apply(Cell args, Env f)\n  throws Exception\n  {");
    out.println("    Cell t = args;");
    out.println("    Obj  tmp;");
    for (int i=0; i<java_inp_type.length; i++)
      {
        out.println("    if (t == null) { throw new SchemeError(\""
                    + scm_name + " expects "
                    + java_inp_type.length +
                    " arguments\"); }");
        out.println("    tmp = (t.car!=null)?t.car.eval(f):null; t = t.cdr;");

        if (java_inp_type[i].equals("String")) { mode = 0; }
        else if ((java_inp_type[i].equals("short")) ||
                 (java_inp_type[i].equals("int")) ||
                 (java_inp_type[i].equals("long"))) { mode = 1; }
        else if ((java_inp_type[i].equals("float")) ||
                 (java_inp_type[i].equals("double"))) { mode = 3; }

        else { mode = 2; }

        switch(mode)
          {
          case 0:               // String
            out.println
              ("    if ((tmp != null) && !(tmp instanceof Selfrep))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a String for arg #" + (i+1) +
               "\"); }");
            out.println
              ("    String arg" + i + " = (tmp!=null)?((Selfrep)tmp).val:null;");
            break;
          case 1:               // number
          case 3:
            out.println
              ("    if (!(tmp instanceof Selfrep))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a number for arg #" + (i+1) +
               "\"); }");
            if (mode == 1)
              {
                out.println
                  ("    "+java_inp_type[i]+" arg" + i +
                   " = (" + java_inp_type[i] + ")(Math.round(((Selfrep)tmp).num));");
              }
            else
              {
                out.println
                  ("    "+java_inp_type[i]+" arg" + i +
                   " = (" + java_inp_type[i] + ")(((Selfrep)tmp).num);");
              }
                
            break;
          default:              // primnode
            out.println
              ("    if ((tmp != null) && !(tmp instanceof primnode))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a " + java_inp_type[i] +
               " for arg #" + (i+1) + "\"); }");
            out.println
              ("    if ((tmp != null) && !((((primnode)tmp).val) instanceof " + 
               java_inp_type[i] + ")) { throw new SchemeError(\"" +
               scm_name + " expects a " + java_inp_type[i] +
               " for arg #" + (i+1) + "\"); }");
            out.println
              ("    "+java_inp_type[i]+" arg" + i +
               " = (tmp != null)?(" + java_inp_type[i] + ")(((primnode)tmp).val):null;");
            break;
          }
      }

                                // Now create the new object
    out.print("    return new primnode(new " +
              java_name + "(");

    if (java_inp_type.length != 0)  out.print("arg0");

    for (int i=1; i<java_inp_type.length; i++)
      { out.print(", arg" + i); }
    out.println("));\n  }");
    out.println("  public String toString()");
    out.println("  { return (\"<#" + scm_name + "#>\"); }");
    out.println("}");
  }
}

class procinfo
                                // Create simple procedures
                                // automatically
{
  String java_name;
  String scm_name;
  String java_inp_type[];

  procinfo(String sname, String jname, String jit[])
  {
    java_name = jname;
    scm_name = sname;
    java_inp_type = jit;
  }

  void write(PrintStream out)
  {
    int mode;

    out.println("//Autogenerated by procinfo on " + new Date());
    out.println
      ("class scm" + java_name + " extends Procedure implements Obj\n{");
    out.println
      ("  Obj apply(Cell args, Env f)\n  throws Exception\n  {\n");
    out.println
      ("    Cell t = args;");
    out.println
      ("    Obj tmp;");
    for (int i=0; i<java_inp_type.length; i++)
      {
        out.println
          ("    if (t == null) { throw new SchemeError(\""
           + scm_name + " expects "
           + java_inp_type.length +
           " arguments\"); }");
        out.println
          ("    tmp = (t.car!=null)?t.car.eval(f):null; t = t.cdr;");

        if (java_inp_type[i].equals("String")) { mode = 0; }
        else if ((java_inp_type[i].equals("short")) ||
                 (java_inp_type[i].equals("int")) ||
                 (java_inp_type[i].equals("float")) ||
                 (java_inp_type[i].equals("double")) ||
                 (java_inp_type[i].equals("long"))) { mode = 1; }
        else { mode = 2; }

        switch(mode)
          {
          case 0:               // String
            out.println
              ("    if ((tmp != null) && !(tmp instanceof Selfrep))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a String for arg #" + (i+1) +
               "\"); }");
            out.println
              ("    String arg" + i + " = (tmp!=null)?((Selfrep)tmp).val:null;");
            break;
          case 1:               // number
            out.println
              ("    if (!(tmp instanceof Selfrep))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a number for arg #" + (i+1) +
               "\"); }");
            out.println
              ("    "+java_inp_type[i]+" arg" + i +
               " = (" + java_inp_type[i] + ")(((Selfrep)tmp).num);");
            break;
          default:              // primnode
            out.println
              ("    if ((tmp != null) && !(tmp instanceof primnode))" +
               " { throw new SchemeError(\"" +
               scm_name + " expects a " + java_inp_type[i] +
               " for arg #" + (i+1) + "\"); }");
            out.println
              ("    if ((tmp != null) && !((((primnode)tmp).val) instanceof " + 
               java_inp_type[i] + ")) { throw new SchemeError(\"" +
               scm_name + " expects a " + java_inp_type[i] +
               " for arg #" + (i+1) + "\"); }");
            out.println
              ("    "+java_inp_type[i]+" arg" + i +
               " = (tmp != null)?(" + java_inp_type[i] + ")(((primnode)tmp).val):null;");
            break;
          }
      }
                                // now call the method
    out.print("    arg0." + java_name + "(arg1");
    for (int i=2; i<java_inp_type.length; i++)
      { out.print(", arg" + i); }
    out.println(");\n  return null;\n  }");
    out.println("  public String toString()");
    out.println("  { return (\"<#" + scm_name + "#>\"); }");
    out.println("}");
  }
}

class autogen implements jas.RuntimeConstants
{
  
  static String procs[][] =
    {
                                // Manipulate class env
      {"ClassEnv", "CP"}, {"jas-class-addcpe", "addCPItem"},
      {"ClassEnv", "Var"}, {"jas-class-addfield", "addField"},
      {"ClassEnv", "CP"}, {"jas-class-addinterface", "addInterface"},
      {"ClassEnv", "CP"}, {"jas-class-setclass", "setClass"},
      {"ClassEnv", "CP"}, {"jas-class-setsuperclass", "setSuperClass"},
      {"ClassEnv", "short", "String", "String", "CodeAttr", "ExceptAttr"},
                          {"jas-class-addmethod", "addMethod"},
      {"ClassEnv", "short"}, {"jas-class-setaccess", "setClassAccess"},
      {"ClassEnv", "String"}, {"jas-class-setsource", "setSource"},
      {"ClassEnv", "scmOutputStream"}, {"jas-class-write", "write"},

                                // Add things to exceptions
      {"ExceptAttr", "CP"}, {"jas-exception-add", "addException"},

                                // Manipulate code attrs
      {"CodeAttr", "Insn"}, {"jas-code-addinsn", "addInsn"},
      {"CodeAttr", "short"}, {"jas-code-stack-size", "setStackSize"},
      {"CodeAttr", "short"}, {"jas-code-var-size", "setVarSize"},
      {"CodeAttr", "Catchtable"}, {"jas-set-catchtable", "setCatchtable"},


                                // add things to catchtables
      {"Catchtable", "CatchEntry"}, {"jas-add-catch-entry", "addEntry"},
    };

  static String types[][] =
    {
      {"String"}, {"make-ascii-cpe", "AsciiCP"},
      {"String"}, {"make-class-cpe", "ClassCP"},
      {"String", "String"}, {"make-name-type-cpe", "NameTypeCP"},
      {"String", "String", "String"}, {"make-field-cpe", "FieldCP"},
      {"String", "String", "String"}, {"make-interface-cpe", "InterfaceCP"},
      {"String", "String", "String"}, {"make-method-cpe", "MethodCP"},
      {"int"}, {"make-integer-cpe", "IntegerCP"},
      {"float"}, {"make-float-cpe", "FloatCP"},
      {"long"}, {"make-long-cpe", "LongCP"},
      {"double"}, {"make-double-cpe", "DoubleCP"},
      {"String"}, {"make-string-cpe", "StringCP"},
      {"short", "CP", "CP", "ConstAttr"}, {"make-field", "Var"},
      {"CP"}, {"make-const", "ConstAttr"},
      {"String"}, {"make-outputstream", "scmOutputStream"},
      {"String"}, {"make-label", "Label"},
      {}, {"make-class-env", "ClassEnv"},
      {}, {"make-code", "CodeAttr"},
      {}, {"make-exception", "ExceptAttr"},
      {}, {"make-catchtable", "Catchtable"},
      {"Label", "Label", "Label", "CP"}, {"make-catch-entry", "CatchEntry"},
      {"int", "int"}, {"iinc", "IincInsn"},
      {"CP", "int"}, {"multianewarray", "MultiarrayInsn"},
      {"CP", "int"}, {"invokeinterface", "InvokeinterfaceInsn"},
    };

  public static void main(String argv[])
    throws IOException
  {

    PrintStream initer =
      new PrintStream(new FileOutputStream("AutoInit.java"));
    initer.println("package scm;\n\nimport jas.*;");
    initer.println("class AutoInit\n{\n  static void fillit(Env e)\n  {");

                                // Generate types in the system.
    PrintStream doit = new PrintStream(new FileOutputStream("AutoTypes.java"));
    doit.println("package scm;\n\nimport jas.*;");
    for (int x = 0; x<types.length; x += 2)
      {
        typeinfo tp = new typeinfo(types[x+1][0], types[x+1][1], types[x]);
        tp.write(doit);
        initer.println("e.definevar(Symbol.intern(\"" +
                       types[x+1][0] + "\"), new scm" +
                       types[x+1][1] + "());");
      }

                                // Add some simple procedures
    doit = new PrintStream(new FileOutputStream("AutoProcs.java"));
    doit.println("package scm;\n\nimport jas.*;");
    for (int x = 0; x<procs.length; x += 2)
      {
        procinfo p = new procinfo(procs[x+1][0], procs[x+1][1], procs[x]);
        initer.println("e.definevar(Symbol.intern(\"" +
                       procs[x+1][0] + "\"), new scm" +
                       procs[x+1][1] + "());");
        p.write(doit);
      }

    initer.println("  }\n}");
  }
}
