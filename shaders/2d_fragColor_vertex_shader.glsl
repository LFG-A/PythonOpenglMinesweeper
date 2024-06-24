#version 330 core

layout (location=0) in vec2 vertexPos; // x,y
layout (location=1) in vec4 color; // rbga

out vec4 fragColor; // Output color to the fragment shader

void main() {
    gl_Position = vec4(vertexPos, 0.0, 1.0); // Set the position
    fragColor = color; // Pass the color to the fragment shader
}