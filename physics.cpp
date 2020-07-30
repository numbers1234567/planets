/*
'Getter' for physics. It doesn't modify any data, it merely spits back a number.
Pointers must be provided by main program
*/

#include <stdio.h>
#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

struct gravityObjectData {
    // Pure pointers since data is dynamic and I don't want to go through re-setting these
    float x;
    float y;
    float velx;
    float vely;
    float mass;
    float radius;
    int id; // index
};

float gravConstant = 10.;
vector<struct gravityObjectData> gravityObjects;

extern "C" {
/*
Calculates force from gravity of all combined gravityObjects given x and y.
Populates buffers with the force
*/
void getGravForce(int id, float *forcex_buffer, float *forcey_buffer) {
    float forceX = 0;
    float forceY = 0;
    float x = gravityObjects[id].x;
    float y = gravityObjects[id].y;
    float mass = gravityObjects[id].mass;

    for (auto it=gravityObjects.begin(); it != gravityObjects.end(); ++it) {
        if (it->x == x && it->y == y) { // Haha! Division by 0!
            continue;
        }
        float distanceSquared = pow((it->x) - x, 2) + pow((it->y) - y, 2);
        float forceScalar = mass* (it->mass) * gravConstant/distanceSquared;
        if (it->x == x) {
            forceX += forceScalar*abs((it->y) - y)/((it->y) - y);
            continue;
        }
        float x_add = cos(atan((it->y - y)/(it->x - x))) * forceScalar;
        float y_add = cos(atan((it->y - y)/(it->x - x))) * forceScalar;
        if ((it->x > x && x_add < 0) || (it->x < x && x_add > 0)) x_add *= -1;
        if ((it->y > y && y_add < 0) || (it->y < y && y_add > 0)) y_add *= -1;
        forceX += x_add;
        forceY += y_add;
    }
    *forcex_buffer = forceX;
    *forcey_buffer = forceY;
}

/*
Add grav object to calculations. Returned ID is index 
*/
int addGravObject(float x, float y, float velx, float vely, float mass) {
    struct gravityObjectData newData;
    newData.x = x;
    newData.y = y;
    newData.velx = velx;
    newData.vely = vely;
    newData.mass = mass;
    newData.id = gravityObjects.size();
    gravityObjects.push_back(newData);

    return newData.id;
}

void updateData(int id, float x, float y, float velx, float vely, float mass) {
    gravityObjects[id].x = x;
    gravityObjects[id].y = y;
    gravityObjects[id].velx = velx;
    gravityObjects[id].vely = vely;
    gravityObjects[id].mass = mass;
}

}