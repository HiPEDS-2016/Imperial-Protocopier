height=0.0957336;
radius=0.3220551931/2;
cprecent=60;
stlname="mug7_poisson.stl";
translate_vec=[0.05741998, 0.05123826, 0.29631892];
rotate_vec=[-0.99744062, -0.07149975, 0.0];
rotate_deg=-82.5362845431;
scaling=100;


intersection() {
	rotate(rotate_vec*rotate_deg)
	scale([scaling, scaling, scaling]) 
	translate(translate_vec)
	import(stlname, convexity=3);

	translate([0,0,0.5]) 
	cylinder(h = height*scaling, r1 = radius*scaling*(cprecent/100), r2 = radius*scaling*(cprecent/100));
}



