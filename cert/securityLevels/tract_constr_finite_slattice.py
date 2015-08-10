# Inequalities
Ilist = namedtuple('Ilist', ['left', 'right', 'insted'])
# Vars
clist = {} # dict('vars', 'inequality' = [])
# Pointers to inequalities not stisfied in p
NS = namedtuple('NS', ['left', 'right', 'insted'])
# current interpretation
p = {} # dict('var', 'level')
# <= to var
C_var = namedtuple("c_var", ['var, lower'])

def initialize_p(vars, order):
    bottom = get_bottom(order)
    for var in vars:
        P [var] = bottom

def initialize_cvar(vars, inequalities):
    for var in vars: 
        for inequality in inequalities:
            if var == inequality[0] or var == inequality[1]
                C_var

def initialize_clist(var, inequalities):

def initialize_ilist(inequalities):

# removes the head element from ns and returns it after setting the field insted to false 
def pop(): 

# inserta a inequality at the front of ns, updating insted field (if insted is true, insert does nothing)
def inster(i):

# remove i from ns 
def drop(i):

def tract_const_finite_semilattice(inequalities, var, order):
    p = initialize_p(var, order)
    c_var = initialize_cvar(var, inequalities)
    clist = initialize_clist(var, inequalities)
    ilist = initialize_ilist(inequalities)
    