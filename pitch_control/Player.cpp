#include <iostream>
#include "Player.h"
#include <cmath>

namespace football {

    // Default constructor
    Player::Player () {}

    // Overloaded constructor
    Player::Player (int id, float position_x, float position_y, float velocity_x, float velocity_y, float vmax, float reaction_time, float tti_sigma) {
        this->id = id;
        this->position_x = position_x;
        this->position_y = position_y;
        this->velocity_x = velocity_x;
        this->velocity_y = velocity_y;
        this->vmax = vmax;
        this->reaction_time = reaction_time;
        this->tti_sigma = tti_sigma;
        this->PPCF = 0;
        this->time_to_intercept = 0;
    }

    // Destructor
    Player::~Player () {}

    float Player::simple_time_to_intercept(float target_x, float target_y) {
        float r_reaction_x = this->position_x + this->velocity_x * this->reaction_time;
        float r_reaction_y = this->position_y + this->velocity_y * this->reaction_time;
        this->time_to_intercept = this->reaction_time + sqrt(pow(target_x - r_reaction_x, 2) + pow(target_y - r_reaction_y, 2)) / this->vmax;
        return time_to_intercept;
    }

    float Player::probability_intercept_ball(float t) {
        // probability of a player arriving at target location at time 't' given their expected time_to_intercept (time of arrival), as described in Spearman 2018
        float p = 1 / (1. + exp(-M_PI / sqrt(3.0) / this->tti_sigma * (t - this->time_to_intercept)));
        return p;
    }
}