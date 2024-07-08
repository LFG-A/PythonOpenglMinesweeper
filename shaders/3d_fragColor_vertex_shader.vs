#version 330 core

layout (location = 0) in vec3 vertexPosition;
layout (location = 1) in vec4 vertexColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 fragColor;

void main()
{
    vec4 worldPosition = vec4(vertexPosition, 1.0) * model;
    gl_Position = projection * view * worldPosition;
    fragColor = vertexColor;
}
