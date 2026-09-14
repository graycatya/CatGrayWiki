"""Volume-preserving section frames for a forward, rounded mascot wave.

The 41 native skin bones follow the arm's existing cross sections. Their
ordinary TRS keys survive glTF export without runtime curves or morphs.
"""
import math
from mathutils import Vector, Matrix, Quaternion

class WaveArc:
    def __init__(self, points):
        levels=sorted({round(p.z,6) for p in points},reverse=True)
        self.centres=[]
        for z in levels:
            ring=[p for p in points if abs(p.z-z)<1e-5]
            self.centres.append(sum(ring,Vector())/len(ring))
        self.levels=levels
        self.names=[f'ArmArc.R.{i:02d}' for i in range(len(levels))]
        self.lengths=[0.]
        for a,b in zip(self.centres,self.centres[1:]):
            self.lengths.append(self.lengths[-1]+(b-a).length)
        self.stations=[v/self.lengths[-1] for v in self.lengths]

    def bones(self, create):
        for name,p in zip(self.names,self.centres):
            create(name,p,p+Vector((0,0,-.025)),'UpperArm.R')

    def weights(self,p):
        i=min(range(len(self.levels)),key=lambda i:abs(p.z-self.levels[i]))
        weights={}
        for offset,w in [(-1,1/6),(0,2/3),(1,1/6)]:
            name=self.names[max(0,min(len(self.names)-1,i+offset))]
            weights[name]=weights.get(name,0)+w
        return weights

    def target(self,wiggle):
        p0=self.centres[0]
        p1=Vector((.90,-.04,1.08))
        p2=Vector((1.10+.060*wiggle,-.65,1.32))
        p3=Vector((1.16+.180*wiggle,-.82,1.96+.015*wiggle))
        samples=[]
        for i in range(401):
            t=i/400;u=1-t
            samples.append(u**3*p0+3*u*u*t*p1+3*u*t*t*p2+t**3*p3)
        lengths=[0.]
        for a,b in zip(samples,samples[1:]):lengths.append(lengths[-1]+(b-a).length)
        result=[];j=0
        for s in self.stations:
            d=s*lengths[-1]
            while j<len(lengths)-2 and lengths[j+1]<d:j+=1
            f=(d-lengths[j])/(lengths[j+1]-lengths[j])
            result.append(samples[j].lerp(samples[j+1],f))
        return result

    def pose(self,rig,envelope,wiggle):
        if envelope<1e-8:return
        target=self.target(wiggle)
        current=[self.centres[0].copy()]
        # Interpolate directions on arcs, never blend opposite vectors:
        # linear position blending would shorten/collapse the lifted forearm.
        for a,b,c,d in zip(self.centres,self.centres[1:],target,target[1:]):
            rest=b-a;goal=d-c
            q=Quaternion().slerp(rest.normalized().rotation_difference(goal.normalized()),envelope)
            delta=(q@rest.normalized())*((1-envelope)*rest.length+envelope*goal.length)
            current.append(current[-1]+delta)
        for i,(name,rest,p) in enumerate(zip(self.names,self.centres,current)):
            lo=max(0,i-1);hi=min(len(current)-1,i+1)
            tangent=(current[hi]-current[lo]).normalized()
            rest_tangent=(self.centres[hi]-self.centres[lo]).normalized()
            transport=rest_tangent.rotation_difference(tangent)
            # At rest keep approved geometry exact. As the hand rises, orient
            # the ring planes perpendicular to the arc to remove inherited
            # shear in the original horizontally lofted limb.
            perpendicular=Vector((0,0,-1)).rotation_difference(tangent)
            rotation=transport.slerp(perpendicular,envelope)
            deform=Matrix.Translation(p)@rotation.to_matrix().to_4x4()@Matrix.Translation(-rest)
            bind=rig.data.bones[name].matrix_local
            rig.pose.bones[name].matrix_basis=bind.inverted()@deform@bind
