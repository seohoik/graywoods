import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content', // use Astro's built‑in MD/MDX loader
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    pubDate: z.coerce.date(),
    author: z.string().optional(),
    tags: z.array(z.string()).default([]),
    image: z.object({ url: z.string() }).optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = { posts };
